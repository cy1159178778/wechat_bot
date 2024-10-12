import numpy as np
from numba import jit
from scipy.ndimage import label as CCL


class GoAi:
    def __init__(self):
        self.MapL = 19  # 棋盘大小
        self.step = 0  # 步数，为偶数时黑方落子
        self.steps = []  # 每一步的坐标
        self.ko = [0, -1, -1]  # 打劫标志 [flag,x,y]
        self.ko_list = []
        self.board = np.zeros((self.MapL, self.MapL), dtype=np.int16)  # 生成棋盘
        self.board_list = []

    def CalcScore(self, board, y=3, x=3):
        score = 0
        for n, player in enumerate([1 + self.step % 2, 2 - self.step % 2]):  # n=0:mine,n=1:oppo
            board_0 = board == player
            components = CCL(board_0)[0]
            for i in range(int(np.max(components))):
                component = np.where(components == i + 1)
                qi = CalcQi(component, board, self.MapL)  # 气
                count = len(component[0])  # 棋子数
                score += (1.07 - 2.11 * n) * qi
                if count > 6 and qi < 2 and not n:
                    score -= 1000
                if qi < 4:
                    score += (2 * n - 1) * (1.6 - 0.5 * qi) * (1 + count / (9 + n * 16))
            score += (2 * n - 1) * (np.max(components) * 2.11 - np.sum(board == player) * 1.25)

        neighbor8 = board[max(y - 2, 0):min(y + 1, self.MapL), max(x - 2, 0):min(x + 1, self.MapL)]
        coeff = 8 / len(neighbor8) / len(neighbor8[0])
        mine, oppo = (-0.98 + np.sum(neighbor8 == 1 + self.step % 2)) * coeff, np.sum(neighbor8 == 2 - self.step % 2) * coeff
        count = abs((mine - oppo) * 8 / len(neighbor8) / len(neighbor8[0]))
        score -= 0.02 * count
        if count > 1:
            score -= count ** 1.5 / 5
        if mine > 5 and oppo == 0:
            score -= mine / 3

        neighbor24 = board[max(y - 3, 0):min(y + 2, self.MapL), max(x - 3, 0):min(x + 2, self.MapL)]
        coeff = 24 / len(neighbor24) / len(neighbor24[0])
        mine, oppo = (-1 + np.sum(neighbor24 == 1 + self.step % 2)) * coeff, np.sum(neighbor24 == 2 - self.step % 2) * coeff
        count = abs((mine - oppo))
        if count > 1 or np.random.rand() > 0.2:
            score -= 0.01 * count / (1 + self.step / 60)
        if mine > 2 * oppo + 3:
            score -= mine / 3
        if count > 7:
            score -= count

        corner = 0.02 * self.MapL + 3.13 - self.step / 2000
        score += 0.03 / (
                min(abs(y - corner), abs(y - self.MapL - 1 + corner)) + min(abs(x - corner), abs(x - self.MapL - 1 + corner)))
        if min(x, y) == 1 or max(x, y) == self.MapL:
            score += 0.01 * (1 + self.step / 100)
        if x == 1 or x == self.MapL or y == 1 or y == self.MapL:
            try:
                if (x <= 2 and (board[y - 2][x] == board[y][x] == 1 + self.step % 2 and board[y - 1][x] == 2 - self.step % 2)) or \
                        (x >= self.MapL - 1 and (board[y - 2][x - 2] == board[y][x - 2] == 1 + self.step % 2 and board[y - 1][
                            x - 2] == 2 - self.step % 2)) or \
                        (y <= 2 and (board[y][x - 2] == board[y][x] == 1 + self.step % 2 and board[y][x - 1] == 2 - self.step % 2)) or \
                        (y >= self.MapL - 1 and (board[y - 2][x - 2] == board[y - 2][x] == 1 + self.step % 2 and board[y - 2][
                            x - 1] == 2 - self.step % 2)):
                    score += 1.5
            except:
                score += 0.02
        return score

    def auto(self, player=2):
        '''电脑计算下一步棋的最佳位置'''
        # print("auto",end=' ')
        max_score = -np.inf
        tizimax = [0, 0]
        ymax = 1
        xmax = 1
        for i in range(self.MapL):
            for j in range(self.MapL):
                if not self.board[i][j]:
                    temp = self.board.copy()
                    temp[i][j] = player
                    tizis = self.tizi(temp)
                    if not tizis[1] and tizis[0]:
                        temp[i][j] = 0
                        score = -9999
                    elif self.ko[0] and abs(j - self.ko[1] + 1) + abs(i - self.ko[2] + 1) == 1:
                        temp[i][j] = 0
                        temp[self.ko[2] - 1][self.ko[1] - 1] = 2 - self.step % 2
                        score = -9999
                    else:
                        score = self.CalcScore(temp, i + 1, j + 1) + np.random.rand() * 0.002
                    if max_score < score:
                        max_score = score
                        ymax = i + 1
                        xmax = j + 1
                        tizimax = tizis
                else:
                    pass
        if tizimax == [1, 1]:
            self.ko = [1, xmax, ymax]
        else:
            self.ko = [0, -1, -1]

        # print("max_score:",int(max_score),"(x,y):",xmax,ymax)
        return ymax, xmax

    def move(self, y, x):
        '''走一步棋'''
        # print("move",end=' ')
        i, j = y - 1, x - 1
        self.board[i][j] = self.step % 2 + 1
        tizis = self.tizi(self.board)
        if tizis[0] == 1 and tizis[1] == 1:
            self.ko = [1, x, y]
        else:
            self.ko = [0, -1, -1]
        self.step += 1
        self.steps.append([y, x])
        self.ko_list.append(self.ko.copy())
        self.board_list.append(self.board.copy())

    def pop(self):
        self.step -= 1
        self.steps.pop()
        self.ko = self.ko_list.pop().copy()
        self.board = self.board_list.pop().copy()

    def tizi(self, board):
        '''提子，返回提子的数量'''
        # print("tizi")
        tizi_nums = [0, 0]
        board_0 = board.copy()
        for n, player in enumerate([1 + self.step % 2, 2 - self.step % 2]):
            board_1 = board_0 == player
            components = CCL(board_1)[0]
            for i in range(int(np.max(components))):
                component = np.where(components == i + 1)
                if CalcQi(component, board, self.MapL) == 0:
                    tizi_nums[n] += np.shape(component)[1]
                    if n:
                        board[component] = 0
        return tizi_nums


@jit
def CalcQi(component, board, MapL):
    '''计算一块棋的气'''
    qi = 0
    zeros = np.where(board == 0)
    for n in range(len(zeros[0])):
        i, j = zeros[0][n], zeros[1][n]
        if i < np.min(component[0]) - 1 or i > np.max(component[0]) + 1:
            continue
        if j < np.min(component[1]) - 1 or j > np.max(component[1]) + 1:
            continue
        exit_flag = 0
        for offset in [[0, -1], [1, 0], [-1, 0], [0, 1]]:
            i2, j2 = i + offset[0], j + offset[1]
            if 0 <= i2 < MapL and 0 <= j2 < MapL:
                for m in range(len(component[0])):
                    if i2 == component[0][m] and component[1][m] == j2:
                        qi += 1
                        if (min(i, j) == 0 or max(i, j) == MapL - 1) and (
                                min(i2, j2) == 0 or max(i2, j2) == MapL - 1):
                            qi += 0.15
                        exit_flag = True
                        break
            if exit_flag:
                break
    return qi


if __name__ == "__main__":
    go_ai = GoAi()
    go_ai.move(16, 16)
    print(go_ai.auto())
    go_ai.pop()
    go_ai.move(16, 16)
    print(go_ai.auto())
