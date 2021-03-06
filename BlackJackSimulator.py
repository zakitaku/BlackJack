import sys
import random

'''
基本となるカードを定義するクラス
rank:カードのランク, suit:カードのスート, value:カードから得る数
'''


# gitテスト用変更点 12345


class Card:
    RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
    SUITS = ('Spade', 'Heart', 'Diamond', 'Club')

    # 初期化
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = int(self.getvalue())

    # ランクを数字に変換する
    def getvalue(self):
        if self.rank == 'A':
            return 11
        elif self.rank == 'J' or self.rank == 'Q' or self.rank == 'K':
            return 10
        else:
            return self.rank


'''
Cardクラスからデッキを作成するクラス
使用するデッキの数と、デッキのシャッフル、使用している山札を担当する
実際のカードが入っているのはDeckの中のCardsなので注意すること
'''


class Deck:
    CARDS = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]
    Cards = []
    BaseDeck = []
    for rank in Card.RANKS:
        for suit in Card.SUITS:
            BaseDeck.append(Card(rank, suit))  # オブジェクト共有を回避するための基本となる一デッキ

    # 初期化
    # decNumの数だけデッキを使用する
    def __init__(self, decNum):
        basedec = []
        while (decNum > 0):
            basedec += self.BaseDeck
            decNum -= 1
        self.Cards = basedec
        self.current = 0

    # シャッフルをする関数
    # shuffleNumに入れる数字によりシャッフルの回数を制御
    def shuffle(self, shuffleNum):
        self.current = 0
        while shuffleNum > 0:
            cut1 = random.randrange(0, len(self.Cards) / 2)
            cut2 = random.randrange(len(self.Cards) / 2, len(self.Cards))
            temp = self.Cards[cut1]
            self.Cards[cut1] = self.Cards[cut2]
            self.Cards[cut2] = temp
            shuffleNum -= 1
        print("*** deck shuffled ***")


'''
ゲーム参加者を表すスーパークラス
プレイヤーとディーラーとで共通のアクションを定義していく
'''


class GamePlayer:

    # 初期化関数
    def __init__(self):
        self.cards = []
        self.total = 0
        self.acetotal = 0
        self.usedace = 0
        self.burst = False
        self.naturalbj = False
        self.normalbj = False

    # 　子オブジェクトから呼び出せる初期化関数
    def initialize(self):
        self.cards = []
        self.total = 0
        self.acetotal = 0
        self.usedace = 0
        self.burst = False
        self.naturalbj = False
        self.normalbj = False

    # ゲームプレイヤーの手札の合計値を返す関数
    def totalvalue(self):
        i = 0
        self.total = 0
        self.acetotal = 0
        cardnum = len(self.cards)

        while i < cardnum:
            if (self.cards[i].rank == 'A'):
                self.acetotal += 1
            self.total += self.cards[i].value
            i += 1
        self.total -= 10 * self.usedace

        # プレイヤーのバースト判定の処理
        if (self.total > 21):
            if (self.acetotal - self.usedace > 0):
                self.total -= 10
                self.usedace += 1
                if (self.total > 21):
                    self.burst = True
            else:
                self.burst = True


'''
プレイヤーを定義するクラス
ヒット、スタンドなどのプレイヤーが選択する処理は個々に記述する
name:プレイヤー名, cards:プレイヤー個人の手札, total:プレイヤー個人の手札の合計値,
acetotal:プレイヤーのace所持数でバーストした際などの使用する,burst:Trueでプレイヤーがバーストしていることを示す
'''


class Player(GamePlayer):
    # プレイヤーの初期化
    def __init__(self, name):
        self.name = name
        super().__init__()

    # プレイヤーにカードを配るときに使用する関数
    def dealedcard(self, card):
        self.cards.append(card)

    # プレイヤー側のヒットの処理
    def hit(self, dealer):
        self.dealedcard(dealer.dealcard())
        self.showhands()

    # プレイヤー側のスタンドの処理
    def stand(self):
        # self.showhands()
        pass

    # プレイヤ－側のダブルダウンの処理
    def doubledown(self, dealer):
        self.hit(dealer)

    # プレイヤー側のスプリットの処理
    def split(self):
        pass

    # 自身の手札を表示するUI
    def showhands(self):
        self.totalvalue()
        print("---hands---")
        for x in self.cards:
            print('/', x.suit, x.rank)
        print("---total---: ", self.total, "\n")


'''
ディーラーを定義するクラス
ディーラーがデッキを管理しているイメージなのでディーラークラスの中にデッキを作成している
カードを配る処理はこのクラスに記述していく
'''


class Dealer(GamePlayer):
    # ディーラーの初期化
    def __init__(self, deckNum):
        self.deck = Deck(deckNum)
        # ディーラーがシャッフルする回数。今回は10000回シャッフルする。
        self.shufflenum = 10000
        self.deck.shuffle(deckNum * self.shufflenum)
        super().__init__()

    # カードを配る関数
    def dealcard(self):
        card = self.deck.Cards[self.deck.current]
        self.deck.current += 1
        return card

    # 一番最初にカードを配る際の関数
    def firstdeal(self, player):
        super().__init__()
        for x in player:
            x.initialize()
        firstdeal = 2
        while firstdeal > 0:
            self.cards.append(self.dealcard())
            for x in player:
                x.cards.append(self.dealcard())
            firstdeal -= 1

    # 合計が17を超えるまで続ける処理
    def continuehit(self):
        self.totalvalue()
        while (self.total < 17):
            self.cards.append(self.dealcard())
            self.totalvalue()

        print("dealer hands: ", end="")
        for x in self.cards:
            print(x.suit, x.rank, ",", end="")
        print("total: ", self.total)


'''
ゲームを管理するクラス
主にゲームの勝敗に関連する事柄を管理するのでデッキ自体の操作などは行わない
'''


class GameManager:
    def __init__(self, players, dealer):
        self.players = players
        self.dealer = dealer
        self.checkdeal = True

    # 各プレイヤーとディーラーとの間で勝敗を決める
    def judge(self):
        for x in self.players:
            self.checkblackjack(x)
        self.checkblackjack(self.dealer)
        for player in self.players:
            if player.burst == True:
                print(player.name, "lose (player burst)")
                return "lose"
            elif player.burst == False and self.dealer.burst == True:
                print(player.name, "win (dealer burst)")
                return "win"
            elif player.total > self.dealer.total:
                print(player.name, "win (player>dealer)")
                return "win"
            elif player.total < self.dealer.total:
                print(player.name, "lose (player<dealer)")
                return "lose"
            elif player.total == self.dealer.total:
                if player.naturalbj and self.dealer.naturalbj:
                    print(player.name, "draw (natural vs natural)")
                    return "draw"
                elif player.naturalbj and self.dealer.normalbj:
                    print(player.name, "win (natural vs normal)")
                    return "win"
                elif player.normalbj and self.dealer.naturalbj:
                    print(player.name, "lose (normal vs natural)")
                    return "lose"
                elif player.normalbj and self.dealer.normalbj:
                    print(player.name, "draw (normal vs normal)")
                    return "draw"
                else:
                    print(player.name, " draw (player==dealer)")
                    return "draw"

    # ナチュラルブラックジャックとノーマルブラックジャックを判別する関数
    # 入力にプレイヤー個人またはディーラ－個人を与える
    def checkblackjack(self, player):
        if (player.total == 21):
            if (len(player.cards) == 2):
                player.naturalbj = True
            else:
                player.normalbj = True


'''
メイン関数
ゲーム全体の流れをここに記述する 
プレイヤーの追加はここで手動で行ってください
'''


def main():
    # プレイヤーを作成
    p1 = Player("player1")
    #    p2 = Player("player2")
    #    players = [p1, p2]

    # ゲームに参加するプレイヤーを表現
    players = [p1]

    # ディーラーの作成
    # 引数はゲームに使用するデッキの数を表現
    dealer = Dealer(1)

    # カットカードを表現
    # 今回はデッキの半分の位置にカットカードを固定している
    cutcard = len(dealer.deck.Cards) / 2

    # txtデータとして出力するものをstring形式で初期化
    outtxt = ""

    # ゲーム全体のループ回数
    # hogeは現在のループ回数を表現するために作成したものなので消してしまっても特に影響はない
    loopnum = 50
    hoge = loopnum + 1

    # 参照するベーシックストラテジーの配列を定義
    basicstrategy = [['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],
                     ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],
                     ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],
                     ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],
                     ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],
                     ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],
                     ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],
                     ['h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h', 'h'],
                     ['h', 'h', 's', 's', 's', 'h', 'h', 'h', 'h', 'h'],
                     ['s', 's', 's', 's', 's', 'h', 'h', 'h', 'h', 'h'],
                     ['s', 's', 's', 's', 's', 'h', 'h', 'h', 'h', 'h'],
                     ['s', 's', 's', 's', 's', 'h', 'h', 'h', 'h', 'h'],
                     ['s', 's', 's', 's', 's', 'h', 'h', 'h', 'h', 'h'],
                     ['s', 's', 's', 's', 's', 's', 's', 's', 's', 's'],
                     ['s', 's', 's', 's', 's', 's', 's', 's', 's', 's'],
                     ['s', 's', 's', 's', 's', 's', 's', 's', 's', 's'],
                     ['s', 's', 's', 's', 's', 's', 's', 's', 's', 's'],
                     ['s', 's', 's', 's', 's', 's', 's', 's', 's', 's'],
                     # ここからはAがある場合のストラテジー表
                     ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
                     ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
                     ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
                     ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
                     ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
                     ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
                     ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
                     ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
                     ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
                     ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H']
                     ]

    print("wellcome!")

    # メインループ
    while True:
        # UI用のプリント文
        print('--------------------------------------------------------------\n')
        print('---' + str(hoge - loopnum) + '---')

        # ゲームを始める前にデッキの中からカットカードが出てきているかを確認し、出てきていれば、デッキをシャッフルする
        if (dealer.deck.current > cutcard):
            dealer.deck.shuffle(dealer.shufflenum)

        # GameManagerの初期化
        gamemanager = GameManager(players, dealer)

        # ディーラーが各プレイヤー（自身含む）に初期カードを配る
        dealer.firstdeal(players)

        # ディーラーのアップカードとプレイヤーのアップカードを表示するUI部分
        for player in players:
            player.totalvalue()
        print("dealer up card :", dealer.cards[0].suit, dealer.cards[0].rank)
        outtxt += "dealer---" + dealer.cards[0].suit + dealer.cards[0].rank + "\n"
        for x in players:
            print(x.name, "up card ", end="")
            outtxt += x.name + "---"
            j = 0
            while j < 2:
                print("/", x.cards[j].suit, x.cards[j].rank, end=" ")
                outtxt += x.cards[j].suit + x.cards[j].rank + ","
                j += 1
            outtxt += "\n"
            print(" total -", x.total)
        print("")

        # 各プレイヤーに対して選択肢を提示する
        for player in players:
            while 1:
                '''
                手動で操作する際の処理
                print(player.name, "turn")
                for card in player.cards:
                    print("/", card.suit, card.rank)
                print("total - ", player.total)
                print("press: HIT = H, STAND = S, DOUBLEDOWN = D")
                usermessage = input()
                '''

                # プレイヤーの選択はベーシックストラテジーに沿って行われるものとする
                # プレイヤーの手札にA(11)が残っている場合
                if player.acetotal - player.usedace > 0:
                    usermessage = basicstrategy[player.cards[0].value + player.cards[1].value + 5][dealer.cards[0].value - 2]
                # プレイヤーの手札にA(11)が残っていない場合
                else:
                    usermessage = basicstrategy[player.total - 4][dealer.cards[0].value - 2]

                # プレイヤーの選択による行動の分岐を記述
                # プレイヤーがヒットを選択した場合
                if usermessage == 'H' or usermessage == 'h':
                    print("hit\n")
                    outtxt += "hit\n"
                    player.hit(dealer)
                    if (player.burst == True):
                        break
                # プレイヤーがスタンドを選択した場合
                elif usermessage == 'S' or usermessage == 's':
                    print("stand\n")
                    outtxt += "stand\n"
                    player.stand()
                    break
                # プレイヤーがダブルダウンを選択した場合
                elif usermessage == 'D' or usermessage == 'd':
                    player.doubledown(dealer)
                    break
                else:
                    print("you can chose H or S or D")

        # ディーラーは17を超えるまでヒットを続ける
        dealer.continuehit()

        # 勝敗を判定する
        outtxt += gamemanager.judge() + "\n"

        # ループの処理
        loopnum -= 1
        if (loopnum == 0):
            file = open('test.txt', 'w')
            file.writelines(outtxt)
            break
        else:
            print("\n")
            outtxt += "\n"


# デッキ確認用関数
def showdeck():
    dealer = Dealer(2)
    i = 0
    for x in dealer.deck.Cards:
        print(i + 1, x.suit, x.rank)
        i += 1


if __name__ == "__main__":
    main()
#  showdeck()
