import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--area", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)

    args = parser.parse_args()


    area = args.area 
    model = args.model
    # area = "Subtitles"
    # model = "mbart"

    data_folder = f"../../data/{area}"
    f = open(f"{data_folder}/translation/{model}/en_mu_translations_jiebacut.txt", "r")
    zhlines = f.readlines()
    f.close()

    with open(f"{data_folder}/en_mu.txt", "r") as f:
        enlines = f.readlines()

    f_Mut_en = open(f"{data_folder}/Com_Mutated.en", "w")
    f_Ori_zh = open(f"{data_folder}/Com_Original.zh", "w")
    f_Mut_zh = open(f"{data_folder}/Com_Mutated.zh", "w")
    f_Ori_en = open(f"{data_folder}/Com_Original.en", "w")
    f_Ori_O = open(f"{data_folder}/Com_oracle.zh", "w")


    for i in range(len(enlines)):
        en = enlines[i].strip() + "\n"
        zh = zhlines[i].strip() + "\n"
        if i % 2 == 0:
            f_Ori_en.write(en)
            f_Ori_zh.write(zh)
        elif i % 2 == 1:
            f_Mut_en.write(en)
            f_Mut_zh.write(zh)
            f_Ori_O.write(zh)

    f_Mut_en.close()
    f_Mut_zh.close()
    f_Ori_zh.close()
    f_Ori_en.close()
    f_Ori_O.close()
    
