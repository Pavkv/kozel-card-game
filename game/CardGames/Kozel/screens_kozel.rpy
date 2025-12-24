screen kozel():
    if card_game.state in ["player_turn", "player_defend", "player_drop"]:
        $ table_qualifiers = card_game.table.qualifier_set
        $ table_has_cards = len(card_game.table.table) > 0
        $ previous_player = card_game.players[card_game.get_player_index(card_game.previous_player())]
        $ player_has_same_number_of_cards = len(card_game.player.hand) == len(previous_player.hand)
        $ no_legal_follow_up = not any(suit in {card.suit for card in card_game.player.hand} for suit in table_qualifiers)

        if ((no_legal_follow_up and table_has_cards and player_has_same_number_of_cards)
            or card_game.table.beaten()):
            timer 0.5 action Function(kozel_get_next_defender)

    # player taken cards
    use discard_pile_display_player()

    # opponent taken cards
    if card_game.number_of_opponents == 1:
        use discard_pile_display_opponent()

    use table()

screen discard_pile_display_player():

    $ rotate = 0
    for card in card_game.player.discard:
        add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
            xpos KOZEL_PLAYERS_X
            ypos KOZEL_PLAYER_DISCARD_Y
        $ rotate += 5 if rotate < 45 else -45

screen discard_pile_display_opponent():

    $ rotate = 0
    for card in card_game.opponent.discard:
        add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
            xpos KOZEL_PLAYERS_X
            ypos KOZEL_OPPONENT_DISCARD_Y
        $ rotate += 5 if rotate < 45 else -45