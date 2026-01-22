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


    # ----------------------------
    # Information Getters
    # ----------------------------
    def get_current_turn_text():
        state = card_game.state
        current_turn_text = card_game_state_tl.get(card_game_name, {}).get(state, "—")

        if isinstance(card_game, DurakGame):
            if state == "opponent_turn":
                current_turn_text = card_game.current_turn.name + "\n" + current_turn_text
            elif state in ["opponent_defend", "opponent_take"]:
                current_turn_text = card_game.current_defender.name + "\n" + current_turn_text

        if isinstance(card_game, KozelGame):
            if state in ["opponent_turn", "opponent_defend", "opponent_drop"]:
                current_turn_text = card_game.current_turn.name + "\n" + current_turn_text

        return current_turn_text


    # ----------------------------
    # Action Handlers
    # ----------------------------
    def handle_card_action(card_game, index):
        if isinstance(card_game, DurakGame):
            return "durak_handle_card_click", index
        elif isinstance(card_game, KozelGame):
            return "kozel_handle_card_click", index
        elif isinstance(card_game, ElsGame) and card_game.state == "player_defend":
            return "els_swap_cards_player", index
        elif isinstance(card_game, ElsGame) and card_game.state == "player_give":
            return "els_handle_card_click", index
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
        global selected_attack_card_indexes, hovered_card_index, confirm_take, confirm_turn
        if isinstance(card_game, DurakGame) and (card_game.state == "player_turn" or card_game.state == "opponent_take"):
            confirm_index = 0 if confirm_turn[0] is False and confirm_turn[1] else 1
            confirm_turn[confirm_index] = True
            selected_attack_card_indexes = set()
            hovered_card_index = -1
            durak_get_next_attacker()
        elif isinstance(card_game, DurakGame) and card_game.state == "player_defend":
            card_game.state = "player_take"
            confirm_take = True
            durak_get_next_attacker()
        elif isinstance(card_game, KozelGame) and card_game.state == "player_turn":
            selected_attack_card_indexes = set()
            hovered_card_index = -1
            kozel_get_next_defender()
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
        """
        Return the (x, y) position of a specific card in a player's hand layout.
        Uses the SAME layout as the screen, so animations always start correctly.
        """

        # --- Player ---
        if side_index == 0:
            hand = card_game.player.hand
            layout = player_card_layout

        # --- Opponents ---
        else:
            hand = card_game.players[side_index].hand

            if len(card_game.players) == 2:
                layout = opponent_card_layout
            else:
                layout = compute_opponent_card_layout(side_index, len(hand))

        # Determine index
        if override_index is not None:
            idx = override_index
        else:
            try:
                idx = hand.index(card)
            except ValueError:
                idx = 0  # safe fallback

        # Return position safely
        if idx < len(layout):
            return layout[idx]["x"], layout[idx]["y"]
        else:
            return layout[0]["x"], layout[0]["y"]

    def next_slot_pos(side_index):
        """
        Returns the (x, y) position where the next card would land
        in the specified player's hand (used for animation destination).
        Uses dynamic fan layout for AI opponents.
        """
        hand = card_game.players[side_index].hand
        idx = len(hand)

        if side_index == 0:
            return (PLAYER_HAND_X + idx * HAND_SPACING, PLAYER_HAND_Y)
        else:
            # Compute layout using the dynamic fan layout
            layout = compute_opponent_card_layout(side_index, idx + 1)  # +1 for the "next card"
            return (layout[-1]["x"], layout[-1]["y"])

    def compute_hand_layout():
        """Computes layout for player and all opponents depending on number of players."""
        global player_card_layout, opponent_card_layout, opponent_2_card_layout, opponent_3_card_layout

        screen_w = config.screen_width
        screen_h = config.screen_height

        def layout_horizontal(total, y, max_right_x):
            total_width = CARD_WIDTH + (total - 1) * CARD_SPACING
            max_hand_width = max_right_x - 20
            if total_width <= max_hand_width:
                spacing = CARD_SPACING
                start_x = max((screen_w - total_width) // 2, 20)
            else:
                spacing = (max_hand_width - CARD_WIDTH) // max(total - 1, 1)
                start_x = 20
            return [{"x": start_x + i * spacing, "y": y} for i in range(total)]

        player_card_layout = layout_horizontal(len(card_game.player.hand), 825, 1700)

        num_opponents = len(card_game.players) - 1

        # One opponent — same layout as player, just at the top
        if num_opponents == 1:
            opponent_card_layout = layout_horizontal(len(card_game.opponent.hand), 20, 1680)

        # Multiple opponents — use fan layout
        else:
            for opponent_index in range(1, len(card_game.players)):
                layout = compute_opponent_card_layout(opponent_index, len(card_game.players[opponent_index].hand))
                if opponent_index == 1:
                    opponent_card_layout = layout
                elif opponent_index == 2:
                    opponent_2_card_layout = layout
                elif opponent_index == 3:
                    opponent_3_card_layout = layout

    def compute_opponent_card_layout(opponent_index, num_cards):
        """
        Fan-style layout for opponents (1-based index), centered if fewer than 3 opponents.
        """
        base_y = 50

        # Layout constants
        max_hand_width = 300
        spacing_x = 35
        spacing_between_opponents = 700
        screen_center_x = config.screen_width // 2

        num_opponents = len(card_game.players) - 1

        # Calculate base_x depending on opponent count
        if num_opponents >= 3:
            base_x = 200 + (opponent_index - 1) * spacing_between_opponents
        else:
            total_width = (num_opponents - 1) * spacing_between_opponents
            left_edge = screen_center_x - total_width // 2
            base_x = left_edge + (opponent_index - 1) * spacing_between_opponents

        # Adjust spacing to fit within max width
        total_hand_width = (num_cards - 1) * spacing_x
        if total_hand_width > max_hand_width:
            spacing_x = max_hand_width / max(1, num_cards - 1)
            total_hand_width = (num_cards - 1) * spacing_x

        offset_x = base_x - total_hand_width // 2
        spacing_y = 2

        layout = []
        for i in range(num_cards):
            layout.append({
                "x": offset_x + i * spacing_x,
                "y": base_y + i * spacing_y
            })

        return layout

    def table_card_pos(card):
        """
        Return (x, y) screen position of a card on the table.
        Finds the card's position in the table layout based on index.
        """
        for i, (atk, (beaten, def_card)) in enumerate(card_game.table.table.items()):
            x = 320 + i * min(200, 1280 // max(1, len(card_game.table.table)))
            y = TABLE_Y

            if card == atk:
                return x, y
            elif card == def_card:
                return x, y + 115

        return None  # fallback if card not found

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

    def get_next_draw_side():
        return on_finish_draw_animations.pop(0) if on_finish_draw_animations else None

    # ----------------------------
    # Game Start Function
    # ----------------------------
    def start_card_game(game_class, game_name, num_of_cards=6, game_args=(), game_kwargs={}):
        """
        Initializes any card game with dealing animation setup for multi-player.

        Arguments:
        - game_class: the class of the game (e.g., DurakGame)
        - game_name: string name of the game (e.g., "durak")
        - game_args: optional positional arguments for the game constructor
        - game_kwargs: optional keyword arguments for the game constructor
        """
        global card_game, player_name, opponent_name, biased_draw, card_game_name, last_winner
        global base_cover_img_src, base_card_img_src
        global dealt_cards, is_dealing, deal_cards

#         disable_ingame_controls()

        # Initialize game
        card_game = game_class(player_name, opponent_name, biased_draw, *game_args, **game_kwargs)
        card_game_name = game_name
        base_cover_img_src = base_card_img_src + "/cover.png"

        card_game.start_game(n=num_of_cards, last_winner=last_winner)

        for p in card_game.players:
            print(p.hand)

        lowest_trump_player = None
        lowest_trump_card = None

        for player in card_game.players:
            card = player.lowest_trump_card(card_game.deck.trump_suit)
            if card is None:
                continue

            if (
                lowest_trump_card is None or
                Card.rank_values[card.rank] < Card.rank_values[lowest_trump_card.rank]
            ):
                lowest_trump_card = card
                lowest_trump_player = player

        print(lowest_trump_player, lowest_trump_card)

        if isinstance(card_game, KozelGame):
            card_game.sort_players_by_hand_suit()

        compute_hand_layout()

        # Prepare deal animation for all players
        dealt_cards = []
        is_dealing = True
        deal_cards = True

        delay = 0.0
        for side_index, player in enumerate(card_game.players):
            for i in range(len(player.hand)):
                dealt_cards.append({
                    "owner": side_index,  # side_index (0 = player, 1+ = opponents)
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
        if sort_hand and isinstance(card_game, KozelGame):
            card_game.sort_players_by_hand_suit()
        elif sort_hand:
            player.sort_hand(card_game.deck.trump_suit)
        compute_hand_layout()
        if isinstance(on_finish, str):
            resolve_on_finish(on_finish)

    def draw_anim(side, target_count=6, sort_hand=False, step_delay=0.1, on_finish=None):
        """
        Animate drawing cards for the given side (0 = player, 1+ = opponents)
        until the hand has `target_count` cards or the deck is empty.

        Handles animation first, then updates the actual hand after animation.
        """
        table_animations[:] = []

        player = card_game.players[side]
        bias_key = "player" if side == 0 else "opponent"

        # Precompute number of cards to draw
        num_to_draw = min(target_count - len(player.hand), len(card_game.deck.cards))
        anim_duration = 0.2
        d = 0.1  # Initial delay

        drawn_cards = []

        for i in range(num_to_draw):
            card = card_game.deck.draw_with_bias(
                good_prob=card_game.bias.get(bias_key, 0.0)  # default 0.0 if not set
            )

            drawn_cards.append(card)

            dest_x, dest_y = next_slot_pos(side)

            # Use face image for player, back image for opponents
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
            kwargs={"sort_hand": sort_hand, "on_finish": on_finish}
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
            from_side (int): index of the donor player (0 = player)
            to_side (int): index of the receiving player (0 = player)
            index (int): index of the card to take from donor
            base_delay (float): delay before animation
            duration (float): animation duration
        """
        donor = card_game.players[from_side]
        taker = card_game.players[to_side]

        if not donor.hand:
            print("Donor has no cards.")
            return

        # Determine source card and its position
        src_card = donor.hand[index] if index < len(donor.hand) else donor.hand[-1]
        sx, sy = hand_card_pos(from_side, src_card)
        dx, dy = next_slot_pos(to_side)

        # Temporarily remove the card from donor for animation purposes
        donor.hand.remove(src_card)
        compute_hand_layout()

        override_img = (
            get_card_image(src_card) if to_side == 0 else base_cover_img_src
        )

        table_animations[:] = [{
            "card": src_card,
            "src_x": sx,
            "src_y": sy,
            "dest_x": dx,
            "dest_y": dy,
            "delay": base_delay,
            "duration": duration,
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
        global hovered_card_index
        table_animations[:] = []

        player = card_game.players[side]

        # Compute total number of table pairs including incoming ones
        existing_pairs = len(card_game.table.table)
        num_incoming = len(cards) if not is_defense else 1  # only 1 defense per slot
        total_table_cards = existing_pairs + (num_incoming if not is_defense else 0)

        # Centered layout math
        max_table_width = 1280
        card_width = CARD_WIDTH
        pair_spacing = min(200, (max_table_width - total_table_cards * card_width) // max(1, total_table_cards - 1)) if total_table_cards > 1 else 0
        total_width = total_table_cards * card_width + (total_table_cards - 1) * pair_spacing if total_table_cards > 1 else card_width
        start_x = (config.screen_width - max_table_width) // 2 + (max_table_width - total_width) // 2

        base_y = 375

        for i, card in enumerate(cards):
            if not is_defense and not skip_check and not card_game.table.can_append(card):
                print("Cannot append card to table:", card)
                continue

            src_x, src_y = hand_card_pos(side, card)

            # 👉 For attack: each card goes to its own new slot
            if not is_defense:
                slot_offset = slot_index + i  # i-th new attack card
                dest_x = start_x + slot_offset * (card_width + pair_spacing)
                dest_y = base_y
            else:
                # 👉 For defense: all go to same slot_index
                dest_x = start_x + slot_index * (card_width + pair_spacing)
                dest_y = base_y + 120

            override_img = get_card_image(card) if side == 0 else base_cover_img_src

            table_animations.append({
                "card": card,
                "src_x": src_x,
                "src_y": src_y,
                "dest_x": dest_x,
                "dest_y": dest_y,
                "delay": delay + i * 0.2,
                "duration": anim_duration,
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
        """
        Animate discarding pairs of cards for the given player index (0 = player, 1–3 = opponents).
        """
        player = card_game.players[side]
        before = list(player.hand)

        # Actually discard now (only to compute the diff)
        player.discard_pairs_excluding_witch(card_game.deck)

        after = list(player.hand)
        removed = diff_removed(before, after)

        # Restore hand so animation still works visually
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
        s.last_winner = None
        s.use_full_deck = False
        s.num_players = 2

        # els-specific
        s.result_combination_player = None
        s.result_combination_indexes_player = set()
        s.result_combination_opponent = None
        s.result_combination_indexes_opponent = set()
        s.els_us_rules = False

        # durak-specific
        s.selected_card = None
        s.selected_attack_card = None
        s.attack_target = None
        s.selected_attack_card_indexes = set()
        s.selected_card_indexes = set()
        s.confirm_attack = False
        s.confirm_take = False
        s.can_pass = False
        s.passed = False
        s.durak_full_throw = None
        s.durak_passing = False

        # game 21-specific
        s.g21_card_num = 1
        s.g21_aces_low = False

        # witch-specific
        s.made_turn = False

        # kozel specific
        s.confirm_drop = False
        s.drop_queue = []
        s.drop_index = 0