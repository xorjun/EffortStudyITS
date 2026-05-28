import json
from collections import Counter

def validate_test_questions(path):
  with open(path + '/course.json') as f:
    course_metadata = json.load(f)
  topics       = set(course_metadata['topics'])
  competencies = set(course_metadata['competencies'])

  keys = set(course_metadata['curriculum'].keys())
  if keys != topics:
    raise ValueError('topic set and keys of curriculum were not equal. Set difference is: %s' % str((keys - topics) + (topics - keys)))

  # build the task set
  task_set = set()
  for key in keys:
    task_set.update(course_metadata['curriculum'][key])

  q_keys = set(course_metadata['q_matrix'].keys())
  if q_keys != task_set:
    raise ValueError('task set and keys of q_matrix were not equal. Set difference is: %s' % str((q_keys - task_set) + (task_set - q_keys)))

  for task in task_set:
    if len(course_metadata['q_matrix'][task]) != len(competencies):
      raise ValueError('row %s of q matrix has %d entries but should be %d (one per competency)' % (task, len(course_metadata['q_matrix'][task]), len(competencies)))

  correct_answers = {}
  for task in task_set:
    task_path = path + '/task_folder/task_' + task + '/multiple_choice.json'
    with open(task_path) as f:
      try:
        task_data = json.load(f)
      except json.decoder.JSONDecodeError as e:
        print('Error when reading task %s' % task_path)
        raise e
    if len(task_data['possible_choices']) != 4:
      raise ValueError('expected always four choices but got %d for task %s' % (len(task_data['possible_choices']), task))
    if len(task_data['correct_choices']) != 4:
      raise ValueError('expected always four entries in correct_choices but got %d for task %s' % (len(task_data['correct_choices']), task))
    if len(task_data['choice_explanations']) != 4:
      raise ValueError('expected always four entries in choice_explanations but got %d for task %s' % (len(task_data['choice_explanations']), task))
    num_correct = 0
    for i in range(4):
      if task_data['correct_choices'][i] == True:
        if not ('This would have been the correct answer.' in task_data['choice_explanations'][i]):
          print('warning: choice %d was correct for task %s in test %s but the choice explanation was: %s' % (i, task, path, task_data['choice_explanations'][i]))
        num_correct += 1
        correct_answers[task] = i
    if num_correct != 1:
      raise ValueError('expected always one correct choice but got %d for task %s' % (num_correct, task))

  return correct_answers

pre  = validate_test_questions('pre_test')
mid  = validate_test_questions('mid_test')
post = validate_test_questions('post_test')

import numpy as np

tasks = ['proba_dice', 'proba_joint_conditional', 'proba_independence',
  'stats_p_value', 'stats_test', 'stats_formulae',
  'pca_eigenvalues', 'pca_component', 'pca_fa',
  'clust_fitting', 'clust_implementation', 'clust_agglomerative',
  'logistic_irt', 'logistic_implementation', 'logistic_pfa',
  'markov_chain', 'markov_bkt_derivation', 'markov_implementation',
  'deep_training', 'deep_vae', 'deep_dkt',
  'rec_collaborative_filtering', 'rec_matrix_factorization', 'rec_cold_start'
]

C_mat    = np.zeros((len(tasks), 3))
prefixes = ['', 'mid_', 'post_']
dicts    = [pre, mid, post]

for j in range(len(prefixes)):
  counts = Counter()
  for i in range(len(tasks)):
    C_mat[i, j] = dicts[j][prefixes[j] + tasks[i]]
    counts[C_mat[i, j]] += 1
  options = ['a', 'b', 'c', 'd']
  print_str = prefixes[j] + ': '
  for k in range(len(options)):
    print_str += '%s: %d, ' % (options[k], counts[float(k)])
  print(print_str)

for i in range(len(tasks)):
  print('%s\t:%s' % (tasks[i], str(C_mat[i, :])))






