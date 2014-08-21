#!/bin/bash

echo "Starting to run mallet for topic modeling"

rm ./guide_data/.DS_Store

./mallet-2.0.7/bin/mallet import-dir --config input_mallet.config --extra-stopwords word_files/extra_stopwords.txt --stoplist-file word_files/ExtraWords.txt

./mallet-2.0.7/bin/mallet train-topics --config infer_mallet.config

python SaveTopicModel.py
python WriteGuideToData.py
