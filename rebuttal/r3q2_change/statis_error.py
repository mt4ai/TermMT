
import json
import os
import time


# plt.rcParams['font.size'] = 26

pic_font_size = 25

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)


if __name__ == "__main__":
    floder_names = ["Subtitles-detect", "Science-detect", "Laws-detect", "News-detect", "Thesis-detect"]
    models = ["google"]
    output_path = "./results"

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    



    error_statis_dict = dict()
    sentence_statis_dict = dict()
    google_error_sentences = []
    bing_error_sentences = []
    mbart_error_sentences = []

    all_sentences = []

    for floder_name in floder_names:
        origin_file_path = f"../results/{floder_name}/metamorphic_items.json"
        origin_items = read_json(origin_file_path)
        sentences = [origin_item["originSentence"] for origin_item in origin_items]
        sentences = list(set(sentences))
        all_sentences.extend(sentences)
        sentence_statis_dict[floder_name] = len( sentences)
    all_sentences = list(set(all_sentences))
    sentence_statis_dict["all"] = len(all_sentences)

    for model in models:
        phrase_infinsert_error_term = []
        phrase_infinsert_error_sentence = []
        phrase_bertinsert_error_term = []
        for floder_name in floder_names:
            file_path = f"../results/{floder_name}/error_{model}_sbert/metamorphic_item_error_gptfiltered.json"
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
        phrase_infinsert_error_term = list(set(phrase_infinsert_error_term))
        phrase_infinsert_error_sentence = list(set(phrase_infinsert_error_sentence))
        phrase_bertinsert_error_term = list(set(phrase_bertinsert_error_term))

        error_statis_dict[model] = dict()
        error_statis_dict[model]["phrase_infinsert_error_term"] = len(phrase_infinsert_error_term)
        error_statis_dict[model]["phrase_infinsert_error_sentence"] = len(phrase_infinsert_error_sentence)
        error_statis_dict[model]["phrase_bertinsert_error_term"] = len(phrase_bertinsert_error_term)
    google_error_sentences = list(set(google_error_sentences))
    bing_error_sentences = list(set(bing_error_sentences))
    mbart_error_sentences = list(set(mbart_error_sentences))
    error_statis_dict["google"]["all"] = len(google_error_sentences)

        



            
    


    write_json(sentence_statis_dict, f"{output_path}/sentence_statis.json")
    write_json(error_statis_dict, f"{output_path}/error_nofilter_statis.json")