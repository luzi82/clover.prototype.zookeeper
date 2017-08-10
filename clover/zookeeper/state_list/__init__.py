import numpy as np
import os

from zookeeper_screen_recognition import classifier_cp
from clover.zookeeper import bot

IMG_SHAPE = (bot.VIDEO_SIZE[1], bot.VIDEO_SIZE[0], 3)
DUMMY_IMG = np.zeros(IMG_SHAPE)

def init(bot_logic):
    bot_logic.common_cp_clr = classifier_cp.CpClassifier(os.path.join('dependency','zookeeper_screen_recognition',classifier_cp.MODEL_PATH))
    bot_logic.common_cp_clr.predict(DUMMY_IMG)
