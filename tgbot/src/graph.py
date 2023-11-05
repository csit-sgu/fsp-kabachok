import logging
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger("app")


def create_graph(title, data):
    logger.debug(data)
    data_tuples = list(data.items())
    df = pd.DataFrame(data_tuples, columns=["Timestamp", "Value"])

    sns.lineplot(x="Timestamp", y="Value", data=df)

    plt.title(data)

    image_stream = BytesIO()
    plt.savefig(image_stream, format="png")
    image_stream.seek(0)
    plt.close()

    return image_stream
