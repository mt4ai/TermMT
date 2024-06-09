import venn
import json
import os
import time
import matplotlib.pyplot as plt
import matplotlib

# plt.rcParams['font.size'] = 26

pic_font_size = 25

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

def write_text(string_text, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(string_text)


# def draw_venn_mrs(mr_overlap_dict, mrs, output_path, pic_name):
    
#     labels = dict()
#     for key in mr_overlap_dict.keys():
#         labels[str(key)] = f"{mr_overlap_dict[key]}"
#     fig, ax = venn.venn3(labels, names=mrs)
#     for text_obj in fig.findobj(matplotlib.text.Text):
#         text_obj.set_fontsize(pic_font_size)
#     plt.legend().remove()
#     plt.title(pic_name, fontsize=pic_font_size)
#     plt.tight_layout()
#     plt.savefig(output_path)
#     plt.close()

# def draw_venn_system(google_error_sentences, bing_error_sentences, mbart_error_sentences, output_path, pic_name):
#     labels = venn.get_labels([google_error_sentences, bing_error_sentences, mbart_error_sentences], fill=["number"])
#     fig, ax = venn.venn3(labels, names=["Google", "Bing", "Mbart"])
#     for text_obj in fig.findobj(matplotlib.text.Text):
#         text_obj.set_fontsize(pic_font_size)
#     plt.legend().remove()
#     plt.title(pic_name, fontsize=pic_font_size)
#     plt.tight_layout()
#     plt.savefig(output_path)
#     plt.close()

if __name__ == "__main__":
    floder_names = ["Subtitles-detect", "Science-detect", "Laws-detect", "News-detect", "Thesis-detect"]
    models = ["google", "bing", "mbart"]
    model_names = ["Google", "Bing", "mBART"]
    output_path = "./results/overlap"
    fig=plt.figure(figsize=(12,12))
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    ax_list = [ax1, ax2, ax3, ax4]

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    

    if os.path.exists(f"{output_path}/mr_overlap.json") and os.path.exists(f"{output_path}/system_overlap.json"):
        mr_overlap_dict = read_json(f"{output_path}/mr_overlap.json")
        system_overlap_dict = read_json(f"{output_path}/system_overlap.json")
    else:

        mr_overlap_dict = dict()
        google_error_sentences = []
        bing_error_sentences = []
        mbart_error_sentences = []
        google_allerror_items = []
        bing_allerror_items = []
        mbart_allerror_items = []

        for model in models:
            phrase_infinsert_error_term = []
            phrase_infinsert_error_sentence = []
            phrase_bertinsert_error_term = []
            for floder_name in floder_names:
                file_path = f"../translate-1-sth/results/{floder_name}/error_{model}/metamorphic_item_error_gptfiltered.json"
                items = read_json(file_path)
                for item in items:
                    origin_sentence = item["originSentence"]
                    if model == "google":
                        google_error_sentences.append(origin_sentence)
                    elif model == "bing":
                        bing_error_sentences.append(origin_sentence)
                    elif model == "mbart":
                        mbart_error_sentences.append(origin_sentence)
                    if item["phrase_infinsert_error_term"] == 1:
                        phrase_infinsert_error_term.append(origin_sentence)
                    if item["phrase_infinsert_error_sentence"] == 1:
                        phrase_infinsert_error_sentence.append(origin_sentence)
                    if item["phrase_bertinsert_error_term"] == 1:
                        phrase_bertinsert_error_term.append(origin_sentence)
                    if item["phrase_infinsert_error_term"] == 1 & item["phrase_infinsert_error_sentence"] == 1 & item["phrase_bertinsert_error_term"] == 1:
                        item["floder_name"] = floder_name
                        if model == "google":
                            google_allerror_items.append(item)
                        elif model == "bing":
                            bing_allerror_items.append(item)
                        elif model == "mbart":
                            mbart_allerror_items.append(item)
            mr_overlap_dict[model] = venn.get_labels([phrase_infinsert_error_term, phrase_infinsert_error_sentence, phrase_bertinsert_error_term], fill=["number"])
        
                
        

        system_overlap_dict = venn.get_labels([google_error_sentences, bing_error_sentences, mbart_error_sentences], fill=["number"])

        write_json(google_allerror_items, f"{output_path}/google_allerror_items.json")
        write_json(bing_allerror_items, f"{output_path}/bing_allerror_items.json")
        write_json(mbart_allerror_items, f"{output_path}/mbart_allerror_items.json")
        write_json(mr_overlap_dict, f"{output_path}/mr_overlap.json")
        write_json(system_overlap_dict, f"{output_path}/system_overlap.json")

    pic_font_size = 20
    title_font_size = 25
    # draw venn
    for i in range(3):
        model = models[i]
        model_name = model_names[i]
        labels = mr_overlap_dict[model]
        ax = venn.venn3_ax(ax_list[i], labels, names=["MR1","MR2","MR3"], legend=False, fontsize=pic_font_size)
        ax_title = f"Overlap Across {model_name} MRs"
        ax.set_title(ax_title, y=-0.12, fontdict={'fontsize':title_font_size})
    ax = venn.venn3_ax(ax_list[3], system_overlap_dict, names=["Google", "Bing", "mBART"], legend=False, fontsize=pic_font_size)
    ax_title = "Overlap Across NMT Systems"
    ax.set_title(ax_title, y=-0.12, fontdict={'fontsize':title_font_size})
    plt.tight_layout()
    plt.savefig(f"{output_path}/venn.pdf")
    # draw_venn_system(google_error_sentences, bing_error_sentences, mbart_error_sentences, f"{output_path}/venn_system.png", "Error Overlap Across NMT Systems")