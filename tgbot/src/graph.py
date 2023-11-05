import datetime
import logging
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.dates import DateFormatter

logger = logging.getLogger("app")


def create_graph(title, data):
    logger.debug(data)
    data_tuples = list(data.items())
    map(lambda x, y: datetime.fromtimestamp(int(x)), data_tuples)
    df = pd.DataFrame(data_tuples, columns=["Time", "Value"])

    sns.lineplot(x="Time", y="Value", data=df)

    plt.title(title)

    ax = plt.gca()
    ax.set_xticklabels([])
    # xticks = ax.get_xticks()
    # ax.set_xticklabels(
    #     [
    #         pd.to_datetime(tm, unit="ms").strftime("%Y-%m-%d\n %H:%M:%S")
    #         for tm in xticks
    #     ],
    # )

    # date_format = DateFormatter("%H:%M:%S")
    # ax.xaxis.set_major_formatter(date_format)

    image_stream = BytesIO()
    plt.savefig(image_stream, format="png")
    image_stream.seek(0)
    plt.close()

    return image_stream
