init python:
    import random

    from CardGames.Classes.Card import Card
    from CardGames.Durak.DurakGame import DurakGame
    from CardGames.G21.Game21 import Game21
    from CardGames.Witch.WitchGame import WitchGame
    from CardGames.Els.ElsGame import ElsGame
    from CardGames.Kozel.KozelGame import KozelGame

    # ----------------------------
    # Game Setup Functions
    # ----------------------------
    def get_card_image(card):
        """Returns the image path for a card based on its rank and suit."""
        return base_card_img_src + "/{}_{}.png".format(ranks[card.rank], suits[card.suit])

    def get_opponent_avatar_base():
        """
        Returns a path/displayable for the opponent avatar.
        Supports dict (prefers 'body') or string; falls back to placeholder.
        """
        global card_game_avatar

        if card_game_avatar:
            return card_game_avatar['body']
        else:
            return "images/cards/avatars/empty_avatar.png"

    def opponent_avatar_displayable(size=(150, 150), pad=6, top_pad=6):
        """
        Returns the avatar scaled to fit inside `size` with side padding
        and only top padding (no bottom padding).
        """
        base = get_opponent_avatar_base()

        inner_w = max(1, size[0] - pad * 2)
        inner_h = max(1, size[1] - top_pad)

        avatar = Transform(base, xysize=(inner_w, inner_h))

        box = Fixed(
            xmaximum=size[0], ymaximum=size[1],
            xminimum=size[0], yminimum=size[1]
        )

        positioned_avatar = Transform(avatar, xpos=pad, ypos=top_pad)

        box.add(positioned_avatar)
        return box

    def compute_hand_layout():
        """Computes the layout for player and opponent hands based on the number of cards."""
        global player_card_layout, opponent_card_layout
        def layout(total, y, max_right_x):
            total_width = CARD_WIDTH + (total - 1) * CARD_SPACING
            max_hand_width = max_right_x - 20
            if total_width <= max_hand_width:
                spacing = CARD_SPACING
                start_x = max((1920 - total_width) // 2, 20)
            else:
                spacing = (max_hand_width - CARD_WIDTH) // max(total - 1, 1)
                start_x = 20
            return [{"x": start_x + i * spacing, "y": y} for i in range(total)]
        player_card_layout = layout(len(card_game.player.hand), 825, 1700)
        opponent_card_layout = layout(len(card_game.opponent.hand), 20, 1680)

    def is_card_animating(card):
        for anim in table_animations:
            if anim["card"] == card:
                return True
        return False

    def handle_card_action(card_game, index):
        if isinstance(card_game, DurakGame):
            return "durak_handle_card_click", index
        elif isinstance(card_game, KozelGame):
            return "kozel_handle_card_click", index
        elif isinstance(card_game, ElsGame) and card_game.state == "player_defend":
            return "els_swap_cards_player", index
        return None, None

    def handle_confirm_attack():
        if isinstance(card_game, DurakGame):
            confirm_attack = True
            return "durak_confirm_selected_attack"
        elif isinstance(card_game, KozelGame) and card_game.state == "player_turn":
            confirm_attack = True
            return "kozel_confirm_selected_attack"
        elif isinstance(card_game, KozelGame) and card_game.state == "player_drop":
            return "kozel_player_drop"

    def handle_end_turn():
        global selected_attack_card_indexes, hovered_card_index, confirm_take
        if (isinstance(card_game, DurakGame) or isinstance(card_game, KozelGame)) and card_game.state == "player_turn":
            card_game.state = "end_turn"
            selected_attack_card_indexes = set()
            hovered_card_index = -1
        elif isinstance(card_game, DurakGame) and card_game.state == "player_defend":
            card_game.state = "player_take"
            confirm_take = True
        elif isinstance(card_game, KozelGame) and card_game.state == "player_defend":
            card_game.state = "player_drop"

    # ----------------------------
    # Position Helpers
    # ----------------------------
    def diff_removed(before, after):
        """Return list of (index, card) tuples for removed cards."""
        removed = []
        after_set = set(after)
        for i, c in enumerate(before):
            if c not in after_set:
                removed.append((i, c))
        return removed

    def hand_card_pos(side_index, card, override_index=None):
        """Return the layout position (x, y) of the given card in hand layout."""
        layout = player_card_layout if side_index == 0 else opponent_card_layout
        hand = card_game.player.hand if side_index == 0 else card_game.opponent.hand

        if override_index is not None:
            idx = override_index
        else:
            try:
                idx = hand.index(card)
            except ValueError:
                idx = 0  # fallback index

        return layout[idx]["x"], layout[idx]["y"]

    def next_slot_pos(side_index):
        """Position where the next card would visually land in the hand."""
        hand = card_game.player.hand if side_index == 0 else card_game.opponent.hand
        idx = len(hand)
        return (PLAYER_HAND_X + idx * HAND_SPACING, PLAYER_HAND_Y) if side_index == 0 else (OPPONENT_HAND_X + idx * HAND_SPACING, OPPONENT_HAND_Y)

    # ----------------------------
    # Animation Management
    # ----------------------------
    def resolve_on_finish(name, args=(), kwargs=None):
        """
        Resolve and call a function by string name, with optional args and kwargs.
        """
        if kwargs is None:
            kwargs = {}

        if not isinstance(name, str):
            renpy.log("[WARN] resolve_on_finish got non-string: {}".format(name))
            return

        try:
            func = globals().get(name)
            if callable(func):
                func(*args, **kwargs)
            else:
                renpy.log("[WARN] No callable found for '{}'".format(name))
        except Exception as e:
            renpy.log("[ERROR] resolve_on_finish({}): {}".format(name, e))

    def show_anim(on_finish=None, args=(), kwargs=None, delay=0.0):
        """
        Shows the animation screen with a callback by name and optional arguments.

        on_finish: string function name
        args: tuple of positional arguments
        kwargs: dict of keyword arguments
        """
        if kwargs is None:
            kwargs = {}

        renpy.show_screen(
            "table_card_animation",
            on_finish=on_finish,
            args=args,
            kwargs=kwargs,
            delay=delay
        )

    def delay_anim(delay=3, on_finish=None, args=(), kwargs=None):
        """
        Delays for `delay` seconds before executing `on_finish` (by name).
        Compatible with show_anim system.

        Parameters:
        - delay: time to wait in seconds
        - on_finish: string name of the function to call
        - args: tuple of arguments for the function
        - kwargs: dictionary of keyword arguments
        """
        if kwargs is None:
            kwargs = {}

        show_anim(
            on_finish=on_finish,
            args=args,
            kwargs=kwargs,
            delay=delay
        )

    # ----------------------------
    # In-Game Control Management
    # ----------------------------
    def disable_ingame_controls():
        """
        Disables in-game menu, skipping, auto-mode, and rollback.
        Immediately stops skipping if active.
        """
        renpy.game.context().fast_skip = False
        renpy.config.allow_skipping = False
        renpy.preferences.afm_enable = False
        renpy.preferences.skip = False
        renpy.config.rollback_enabled = False
        renpy.block_rollback()

    def enable_ingame_controls():
        """
        Ress normal skipping, rollback, and menu behavior after the game ends.
        """
        renpy.game.context().fast_skip = True
        renpy.config.allow_skipping = True
        renpy.config.rollback_enabled = True

    # ----------------------------
    # Game Start Function
    # ----------------------------
    def start_card_game(game_class, game_name, num_of_cards=6, game_args=(), game_kwargs={}):
        """
        Initializes any card game with dealing animation setup.

        Arguments:
        - game_class: the class of the game (e.g., WitchGame)
        - game_name: string name of the game (e.g., "witch")
        - base_cover_src: base path to card back image
        - player_name, opponent_name: names of the players
        - opponent_avatar: avatar image for the opponent
        - biased_draw: optional bias config
        """
        global card_game, player_name, opponent_name, biased_draw, card_game_name, last_winner
        global base_cover_img_src, base_card_img_src
        global dealt_cards, is_dealing, deal_cards

        disable_ingame_controls()

        card_game = game_class(player_name, opponent_name, biased_draw, *game_args, **game_kwargs)
        card_game_name = game_name
        base_cover_img_src = base_card_img_src + "/cover.png"

        if last_winner:
            first_player_selection = last_winner
        elif not last_winner and isinstance(card_game, DurakGame):
            first_player_selection = "lowest_trump"
        else:
            first_player_selection = None

        card_game.select_first_player(first_player_selection=first_player_selection)
        card_game.start_game(n=num_of_cards)
        compute_hand_layout()

        dealt_cards = []
        is_dealing = True
        deal_cards = True

        delay = 0.0
        for i in range(len(card_game.player.hand)):
            dealt_cards.append({
                "owner": "player",
                "index": i,
                "delay": delay
            })
            delay += 0.1

        for i in range(len(card_game.opponent.hand)):
            dealt_cards.append({
                "owner": "opponent",
                "index": i,
                "delay": delay
            })
            delay += 0.1

        renpy.show_screen("card_game_base_ui")

        renpy.jump(game_name + "_game_loop")

    # ----------------------------
    # In Game Animations
    # ----------------------------
    def apply_draw(drawn_cards, player, sort_hand=False, on_finish=None):
        for card in drawn_cards:
            player.hand.append(card)
        if sort_hand:
            player.sort_hand(card_game.deck.trump_suit)
        compute_hand_layout()
        if isinstance(on_finish, str):
            resolve_on_finish(on_finish)

    def draw_anim(side, target_count=6, sort_hand=False, step_delay=0.1, on_finish=None):
        """
        Animate drawing cards for the given side (0 = player, 1 = opponent)
        until the hand has `target_count` cards or the deck is empty.

        This version handles animation first, then updates the actual hand after animation.
        """
        table_animations[:] = []

        player = card_game.player if side == 0 else card_game.opponent
        bias_key = "player" if side == 0 else "opponent"
        target = "hand{}".format(side)

        # Precompute number of cards to draw
        num_to_draw = min(target_count - len(player.hand), len(card_game.deck.cards))
        anim_duration = 0.2
        d = 0.1  # Initial delay

        # We s the cards to be drawn after animation
        drawn_cards = []

        for i in range(num_to_draw):
            card = card_game.deck.draw_with_bias(
                good_prob=card_game.bias[bias_key]
            )

            drawn_cards.append(card)

            dest_x, dest_y = next_slot_pos(side)

            override_img = get_card_image(card) if side == 0 else base_cover_img_src

            table_animations.append({
                "card": card,
                "src_x": 13,
                "src_y": DECK_Y + 20,
                "dest_x": dest_x,
                "dest_y": dest_y,
                "delay": d,
                "duration": anim_duration,
                "override_img": override_img,
            })

            d += step_delay

        show_anim(
            on_finish="apply_draw",
            args=(drawn_cards, player),
            kwargs={"sort_hand": True, "on_finish": on_finish}
        )

    def after_take(taker, donor, src_card, on_finish=None):
        taker.hand.append(src_card)

        if hasattr(taker, 'on_after_take'):
            taker.on_after_take(donor, src_card)

        compute_hand_layout()

        if isinstance(on_finish, str):
            resolve_on_finish(on_finish)

    def take_card_anim(
        from_side,
        to_side,
        index,
        base_delay=0.1,
        duration=0.4,
        on_finish=None
    ):
        """
        Animate a card being taken from one player to another.

        Parameters:
            from_side (int): 0 = player, 1 = opponent (donor)
            to_side (int): 0 = player, 1 = opponent (taker)
            index (int): index of the card to take from donor
            base_delay (float): delay before animation
            duration (float): animation duration
        """
        donor = card_game.player if from_side == 0 else card_game.opponent
        taker = card_game.player if to_side == 0 else card_game.opponent

        if not donor.hand:
            print("Donor has no cards.")
            return

        # Determine source card and its position
        src_card = donor.hand[index] if index < len(donor.hand) else donor.hand[-1]
        sx, sy = hand_card_pos(from_side, src_card)
        dx, dy = next_slot_pos(to_side)

        # Temporarily hide the card from layout (remove from both hands for now)
        donor.hand.remove(src_card)
        compute_hand_layout()

        override_img = get_card_image(src_card) if to_side == 1 else base_cover_img_src

        table_animations[:] = [{
            "card": src_card,
            "src_x": sx,
            "src_y": sy,
            "dest_x": dx,
            "dest_y": dy,
            "delay": base_delay,
            "duration": duration,
            "target": "hand{}".format(to_side),
            "override_img": override_img,
        }]

        show_anim(
            on_finish="after_take",
            args=(taker, donor, src_card),
            kwargs={"on_finish": on_finish}
        )

    def apply_card_moves(player, cards, slot_index=0, is_defense=False, skip_check=False, on_finish=None):
        attack_keys = list(card_game.table.table.keys())
        for i, card in enumerate(cards):
            if skip_check and is_defense:
                if i == 0 and slot_index < len(attack_keys):
                    atk_card = attack_keys[slot_index]
                    card_game.table.beat(atk_card, card)
            elif is_defense:
                if i == 0 and slot_index < len(attack_keys):
                    atk_card = attack_keys[slot_index]
                    if not card_game.table.table[atk_card][0]:
                        card_game.table.beat(atk_card, card)
                else:
                    print("Cannot defend with multiple cards or invalid slot.")
            else:
                if not card_game.table.append(card):
                    print("Invalid attack: card doesn't match table ranks.")
                    continue

            if card in player.hand:
                player.hand.remove(card)

        compute_hand_layout()

        if isinstance(on_finish, str):
            resolve_on_finish(on_finish)

    def play_card_anim(cards, side, slot_index=0, is_defense=False, skip_check=False, on_finish=None, delay=0.5, anim_duration=0.5):
        """
        Animate playing one or multiple cards from the player's or opponent's hand onto the table,
        then update the table structure and remove cards from the hand.

        Arguments:
        - cards: list of Card objects to animate
        - side: 0 for player, 1 for opponent
        - slot_index: index on table (0 for first attack, 1 for next, etc.)
        - is_defense: if True, only one card should be used to defend at given slot
        - delay: delay before first animation starts
        - anim_duration: animation duration per card
        - skip_check: if True, skip validation checks (for forced moves)
        """
        global hovered_card_index

        table_animations[:] = []

        player = card_game.player if side == 0 else card_game.opponent
        base_x = 350 + slot_index * 200
        base_y = 375

        for i, card in enumerate(cards):
            if card is None:
                continue

            # Skip invalid cards for attack
            if not is_defense and not card_game.table.can_append(card):
                print("Cannot append card to table:", card)
                continue

            src_x, src_y = hand_card_pos(side, card)
            dest_x = base_x + i * 40  # Offset for multi-card visual spacing
            dest_y = base_y + 120 if is_defense else base_y

            override_img = get_card_image(card) if side == 0 else base_cover_img_src

            table_animations.append({
                "card": card,
                "src_x": src_x,
                "src_y": src_y,
                "dest_x": dest_x,
                "dest_y": dest_y,
                "delay": delay + i * 0.2,
                "duration": anim_duration,
                "target": "table",
                "override_img": override_img,
            })

        show_anim(
            on_finish="apply_card_moves",
            args=(player, cards, slot_index, is_defense, skip_check),
            kwargs={"on_finish": on_finish}
        )

        hovered_card_index = -1

    def after_discard_pairs(player, on_finish=None):
        player.discard_pairs_excluding_witch(card_game.deck)
        player.shaffle_hand()
        compute_hand_layout()
        if isinstance(on_finish, str):
            resolve_on_finish(on_finish)

    def discard_pairs_anim(side, base_delay=0.0, step=0.05, on_finish=None):
        """Animate discarding pairs of cards for the given side (0=player, 1=opponent)"""
        player = card_game.player if side == 0 else card_game.opponent
        before = list(player.hand)

        # Actually discard now (only to compute the diff)
        player.discard_pairs_excluding_witch(card_game.deck)

        after = list(player.hand)
        removed = diff_removed(before, after)

        # Restore the hand so animation still works visually
        player.hand = list(before)

        table_animations[:] = []

        for i, (idx, card) in enumerate(removed):
            sx, sy = hand_card_pos(side, card, override_index=idx)

            override_img = get_card_image(card) if side == 0 else base_cover_img_src

            anim = {
                "card": card,
                "src_x": sx,
                "src_y": sy,
                "dest_x": DISCARD_X,
                "dest_y": DISCARD_Y,
                "delay": base_delay + i * step,
                "duration": 0.4,
                "target": "discard",
                "override_img": override_img,
            }

            table_animations.append(anim)

        show_anim(
            on_finish="after_discard_pairs",
            args=(player,),
            kwargs={"on_finish": on_finish}
        )

    # ----------------------------
    # Reset Game Function
    # ----------------------------
    def reset_card_game():
        print("Resetting card game state...")
        renpy.hide("els")
        renpy.hide("durak")
        renpy.hide("game21")
        renpy.hide("witch")

        enable_ingame_controls()

        s = store
        
        # base
        s.card_game = None
        s.card_game_name = None
        s.in_game = True
        s.hovered_card_index = -1
        s.dealt_cards = []
        s.is_dealing = False
        s.draw_animations = []
        s.is_drawing = False
        s.table_animations = []
        s.is_table_animating = False
        s.player_card_layout = []
        s.opponent_card_layout = []
        s.biased_draw = None
        s.hovered_card_index_exchange = -1
        s.selected_exchange_card_index = -1

        # els-specific
        s.result_combination_player = None
        s.result_combination_indexes_player = set()
        s.result_combination_opponent = None
        s.result_combination_indexes_opponent = set()

        # durak-specific
        s.selected_card = None
        s.selected_attack_card = None
        s.attack_target = None
        s.selected_attack_card_indexes = set()
        s.selected_card_indexes = set()
        s.confirm_attack = False
        s.confirm_take = False

        # game 21-specific
        s.g21_card_num = 1
        s.g21_aces_low = False

        # witch-specific
        s.made_turn = False

        # kozel specific
        s.confirm_drop = False
        s.kozel_drop_queue = []
        s.kozel_drop_index = 0