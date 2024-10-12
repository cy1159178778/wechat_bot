from datetime import datetime
from sqlmodel import Field, SQLModel


class GameRecord(SQLModel, table=True):
    __tablename__: str = "cchess_game_record"
    __table_args__ = {"extend_existing": True}

    id: str = Field(default="", primary_key=True)
    session_id: str = ""
    start_time: datetime = datetime.now()
    """ 游戏开始时间 """
    update_time: datetime = datetime.now()
    """ 游戏更新时间 """
    player_red_id: str = ""
    """ 红方id """
    player_red_name: str = ""
    """ 红方名字 """
    player_black_id: str = ""
    """ 黑方id """
    player_black_name: str = ""
    """ 黑方名字 """
    start_fen: str = ""
    """ 起始局面FEN字符串 """
    moves: str = ""
    """ 所有移动，ucci形式，以空格分隔 """
    is_game_over: bool = False
    """ 游戏是否已结束 """
