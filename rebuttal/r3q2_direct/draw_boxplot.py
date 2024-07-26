import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd

def read_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    data = read_json("data4boxplot.json")
    df = pd.DataFrame(data)

    # 设置字体大小
    plt.rcParams.update({'font.size': 13})

    # 绘制箱线图
    # plt.figure(figsize=(8, 10))  # 设置图表大小

    sns.boxplot(x="Type", y="Similarity", data=df, palette="Set2", linewidth=2.5, order=["Correct", "Error"] ,width=0.5)

    # save the plot
    plt.savefig("./results/boxplot.pdf")
    
    