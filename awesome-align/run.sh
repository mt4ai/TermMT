DATA_FILE=./examples/zhen.src-tgt
MODEL_NAME_OR_PATH=./models/model_without_co
OUTPUT_FILE=./output/result.txt

python ./run_align.py \
    --output_file=$OUTPUT_FILE \
    --model_name_or_path=$MODEL_NAME_OR_PATH \
    --data_file=$DATA_FILE \
    --extraction 'softmax' \
    --batch_size 32