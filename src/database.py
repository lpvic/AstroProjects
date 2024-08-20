from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class File(Base):
    __tablename__ = 'Files'
    ID: Mapped[String] = mapped_column(primary_key=True)
    ASIAIR_FILENAME: Mapped[String] = mapped_column(String(256))
    IMAGETYP: Mapped[String] = mapped_column(String(5))
    DATE_OBS: Mapped[DateTime] = mapped_column(DateTime())
    SESSION: Mapped[String] = mapped_column(String(8))
    SEQUENCE: Mapped[Integer] = mapped_column(Integer())
    FRAME: Mapped[Integer] = mapped_column(Integer())
    INSTRUME: Mapped[String] = mapped_column(String(32))
    FILTER: Mapped[String] = mapped_column(String(8))
    EXPOSURE: Mapped[Float] = mapped_column(Float())
    XBINNING: Mapped[Integer] = mapped_column(Integer())
    GAIN: Mapped[Integer] = mapped_column(Integer())
    SET_TEMP: Mapped[Float] = mapped_column(Float())
    GUIDECAM: Mapped[String] = mapped_column(String(32))
    MOUNT: Mapped[String] = mapped_column(String(32))
    TELESCOP: Mapped[String] = mapped_column(String(64))
    LENS: Mapped[String] = mapped_column(String(16))
    FOCALLEN: Mapped[Integer] = mapped_column(Integer())
    OBJECT: Mapped[String] = mapped_column(String(16))
    OBSERVER: Mapped[String] = mapped_column(String(64))
    SITENAME: Mapped[String] = mapped_column(String(64))
    SITELAT: Mapped[String] = mapped_column(String(16))
    SITELON: Mapped[String] = mapped_column(String(16))


    pass


class Changes(Base):
    __tablename__ = 'Changes'
    id: Mapped[int] = mapped_column(primary_key=True)
    pass
