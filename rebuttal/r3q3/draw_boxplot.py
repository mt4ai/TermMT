import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd

def read_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def draw_boxplot(data, pic_path):
    df = pd.DataFrame(data)
    # 设置字体大小
    plt.rcParams.update({'font.size': 13})



    sns.boxplot(x="Type", y="Score", data=df, palette="Set2", linewidth=2.5, order=["Correct", "Error"] ,width=0.5)
    # save the plot
    plt.savefig(pic_path)

if __name__ == "__main__":


    unite_scores = read_json("./results/unite_scores.json")
    draw_boxplot(unite_scores, "./pics/unite_boxplot.pdf")
    plt.close()
    
    