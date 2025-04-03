# VICE
## Visual Implicit Comparative Evaluation

VICE is a dataset derived from the Natural Language for Visual Reasoning v2 (NLVRv2) dataset. We extract image pairs directly from NLVRv2 and enhance them with our own custom annotations, including questions and answers specifically designed for implicit comparative visual reasoning tasks.

## JSON dataset files
Fields from the oringal NLVRv2 dataset
- sentence: The natural language sentence describing the pair of images for this example.
- left_url: The URL of the left image in the pair.
- right_url: The URL of the right image in the pair.
- label: The label: true or false.
- identifier: The unique identifier for the image, in the format: split-set_id-pair_id-sentence-id. split is the split of the data (train, test, or development). set_id is the unique identifier of the original eight-image set used in the sentence-writing task. pair_id indicates which of the pairs in the set it corresponds to (and is between 0 and 3). sentence-id indicates which of the sentences is associated with this pair (and is either 0 or 1 -- each image pair is associated with at most two sentences).
- writer: The (anonymized) identifier of the worker who wrote the sentence. The identifiers are the same across splits of the data.
- validation: The initial validation judgment, including the anonymized worker ID and their judgment.
- extra_validations: In the development and test sets, this is the set of extra judgments acquired for each example, including the anonymized worker ID and their judgment.
- synset: The synset associated with the example.
- query: The query used to find the set of images. You can ignore the numbers suffixing the query; these uniquely identify image sets for each query.
- directory: In the train set, this represents the assigned directory for each example. There are 100 directories in total, and unique image pairs do not appear in multiple directories. This means you can easily sample a validation set from a subset of directories.

Annotation fields:
- open_ended: An open ended question about the image pair
- open_ended_answer: The expected answer to the open ended quesiton