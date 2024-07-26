import sys
import json
import os
import time
import matplotlib.pyplot as plt
import matplotlib
import venn

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

def write_text(string_text, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(string_text)




if __name__ == "__main__":
    areas = ["Laws", "Subtitles", "News", "Science", "Thesis"]
    model = "mbart"
    metric = "lcs"
    input_type = "lcs60"
    output_folder = f"../../data/overlap"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # area = "Subtitles_4"
    # model = "mbart"

    fig=plt.figure(figsize=(18,12))
    ax1 = fig.add_subplot(231)
    ax2 = fig.add_subplot(232)
    ax3 = fig.add_subplot(233)
    ax4 = fig.add_subplot(234)
    ax5 = fig.add_subplot(235)
    ax6 = fig.add_subplot(236)

    ax_list = [ax1, ax2, ax3, ax4, ax5, ax6]

    num_of_same = 0
    num_of_cat = 0
    num_of_ours = 0
    if os.path.exists(f"{output_folder}/overlap_{model}_{metric}_{input_type}.json"):
        result_json = read_json(f"{output_folder}/overlap_{model}_{metric}_{input_type}.json")
    else:
        result_json = dict()
        total_termmt_origins = []
        total_cat_origins = []
        for area in areas:
            termmt_origins = []
            cat_origins = []

            data_folder = f"../../data/{area}"
            cat_items = read_json(f"{data_folder}/{input_type}/metamorphic_items_final_{model}_CAT.json")
            termmt_items = read_json(f"{data_folder}/metamorphic_item_error_gptfiltered.json")
            error_key = "CAT_error_" + metric
            for cat in cat_items:
                if error_key in cat and cat[error_key]:
                    cat_origins.append(cat["originSentence"])
                    total_cat_origins.append(cat["originSentence"])
            
            for termmt in termmt_items:
                termmt_origins.append(termmt["originSentence"])
                total_termmt_origins.append(termmt["originSentence"])

            labels = venn.get_labels([cat_origins, termmt_origins], fill=['number'])
            result_json[area] = labels
        result_json["total"] = venn.get_labels([total_cat_origins, total_termmt_origins], fill=['number'])
        write_json(result_json, f"{output_folder}/overlap_{model}_{metric}_{input_type}.json")
    areas.append("total")
    title_font_size = 30
    fig_font_size = 25
    for area in areas:
        labels = result_json[area]
        

        label_titles = ["CAT", "TermMT"]
        title = area
        if area == "total":
            title = "Total"
        # draw_venn(overlap_dict, shape_lst, output_path, label_titles, title)
        ax = venn.venn2_ax(ax_list[areas.index(area)], labels, names=label_titles, legend=False, fontsize=fig_font_size)
        ax.set_title(title, y=-0.08, fontdict={'fontsize':title_font_size})
        plt.tight_layout()
    fig.tight_layout()
    fig.savefig(f"{output_folder}/baseline_venn_{input_type}.pdf")






        