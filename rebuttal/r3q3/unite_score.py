from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.models.nlp.unite.configuration import InputFormat

pipeline_ins = pipeline(task=Tasks.translation_evaluation, model='iic/nlp_unite_up_translation_evaluation_English_large')

def get_unite_scores(srcs, mts, refs):
    return pipeline_ins({
        'hyp': mts,
        'src': srcs,
        'ref': refs
    })['score']

def get_unite_score(srcsent, mtsent, refsent):
    return pipeline_ins({
        'hyp': [mtsent],
        'src': [srcsent],
        'ref': [refsent]
    })['score'][0]
