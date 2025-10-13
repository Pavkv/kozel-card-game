screen kozel():

    if card_game.table.beaten():
        timer .5 action SetVariable("card_game.state", "end_turn")

    # player taken cards
    use discard_pile_display_player()

    # opponent taken cards
    use discard_pile_display_opponent()

    use table()

screen discard_pile_display_player():

    $ rotate = 0
    for card in card_game.player.discard:
        add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
            xpos DISCARD_PLAYERS_X
            ypos PLAYER_DISCARD_Y
        $ rotate += 5 if rotate < 45 else -45

screen discard_pile_display_opponent():

    $ rotate = 0
    for card in card_game.opponent.discard:
        add Transform(base_cover_img_src, xysize=(CARD_WIDTH, CARD_HEIGHT), rotate=rotate + 15):
            xpos DISCARD_PLAYERS_X
            ypos OPPONENT_DISCARD_Y
        $ rotate += 5 if rotate < 45 else -45