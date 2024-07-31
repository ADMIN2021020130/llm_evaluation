# coding=utf-8
# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Processing data for pretraining."""

import argparse
import json
import multiprocessing
import os
import sys
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
											 os.path.pardir)))
from megatron.data.indexed_dataset import best_fitting_dtype
import time

import torch
try:
	import nltk
	nltk_available = True
except ImportError:
	nltk_available = False

from megatron.tokenizer import build_tokenizer
from megatron.data import indexed_dataset
from scipy.stats import poisson
from glm.collator import GLMPreprocessor
from user.latex_parser import latex_operators, LatexParser
from glm.datasets import BinaryDataset
from glm.data import get_input

# https://stackoverflow.com/questions/33139531/preserve-empty-lines-with-nltks-punkt-tokenizer
class CustomLanguageVars(nltk.tokenize.punkt.PunktLanguageVars):

	_period_context_fmt = r"""
		\S*						  # some word material
		%(SentEndChars)s			 # a potential sentence ending
		\s*					   #  <-- THIS is what I changed
		(?=(?P<after_tok>
			%(NonWord)s			  # either other punctuation
			|
			(?P<next_tok>\S+)	 #  <-- Normally you would have \s+ here
		))"""

class IdentitySplitter(object):
	def tokenize(self, *text):
		return text

class Encoder(object):
	def __init__(self, args):
		self.args = args
		self.parser = LatexParser(simplify=args.simplify_latex)
		self.latex_ops = latex_operators()

	def initializer(self):
		# Use Encoder class as a container for global data
		Encoder.tokenizer = build_tokenizer(self.args)

		if self.args.split_sentences:
			if not nltk_available:
				print("NLTK is not available to split sentences.")
				exit()
			splitter = nltk.load("tokenizers/punkt/english.pickle")
			if self.args.keep_newlines:
				# this prevents punkt from eating newlines after sentences
				Encoder.splitter = nltk.tokenize.punkt.PunktSentenceTokenizer(
					train_text = splitter._params,
					lang_vars = CustomLanguageVars())
			else:
				Encoder.splitter = splitter

		else:
			Encoder.splitter = IdentitySplitter()

	def encode(self, json_line):
		data = json.loads(json_line)
		ids = {}
		for key in self.args.json_keys:
			text = self.text_preprocess(data[key])
			doc_ids = []
			for sentence in Encoder.splitter.tokenize(text):
				sentence_ids = [Encoder.tokenizer.TokenToId("ENC")] + Encoder.tokenizer.tokenize(sentence)
				if len(sentence_ids) > 0:
					doc_ids.append(sentence_ids)
			if len(doc_ids) > 0 and self.args.append_eod:
				doc_ids[-1].append(Encoder.tokenizer.TokenToId("eod"))
			ids[key] = doc_ids
		return ids, len(json_line)
	
	def encode_instruction_data(self, json_line):
		def _encode(text):
			text = self.text_preprocess(text)
			doc_ids = []
			for sentence in Encoder.splitter.tokenize(text):
				sentence_ids = Encoder.tokenizer.tokenize(sentence)
				if len(sentence_ids) > 0:
					doc_ids.extend(sentence_ids)

			return doc_ids

		data = json.loads(json_line)
		if "Input" in data and data["Input"] != "":
			#prompt = "### Instruction:\n{}\n\n### Input:\n{}\n\n### Response:\n".format(
			#	data["Instruction"], data["Input"])
			prompt = "{}\n{}\n".format(data["Instruction"], data["Input"])
		else:
			#prompt = "### Instruction:\n{}\n\n### Response:\n".format(data["Instruction"])
			prompt = "{}\n".format(data["Instruction"])

		response = "{}".format(data["Response"])

		prompt_ids = _encode(prompt)
		response_ids = _encode(response)
		combined_ids = [Encoder.tokenizer.TokenToId('ENC')] \
			+ prompt_ids \
			+ [Encoder.tokenizer.TokenToId('gMASK')] \
			+ response_ids \
			+ [Encoder.tokenizer.TokenToId('eod')]

		if self.args.concat_sequence:
			return {self.args.json_keys[0]: combined_ids}, len(json_line)
		else:
			length_per_samples = self.args.length_per_sample
			#print(Encoder.tokenizer.detokenize(combined_ids))
			if len(combined_ids) < length_per_samples:
				padded_ids = combined_ids + [Encoder.tokenizer.TokenToId('[pad]')] * (length_per_samples - len(combined_ids))
			else:
				padded_ids = [] 
			return {self.args.json_keys[0]: [padded_ids]}, len(json_line)


	def encode_multitask_data(self, json_line):
		def _encode(text):
			try:
				text = self.parser._simply_display_placehold(text)
			except Exception:
				text = text
			text = text.replace("∵", "因为").replace("∴", "所以")
			text = self.text_preprocess(text)
			doc_ids = []
			for sentence in Encoder.splitter.tokenize(text):
				sentence_ids = Encoder.tokenizer.tokenize(sentence)
				if len(sentence_ids) > 0:
					doc_ids.extend(sentence_ids)

			return doc_ids

		def _encode_latex(text):
			try:
				text = self.parser._simply_display_placehold(text)
			except Exception:
				text = text
			text = text.replace("∵", "因为").replace("∴", "所以")
			text = self.text_preprocess(text)
			parsed_seqs = self.parser(text)
			doc_ids = []
			for seq in parsed_seqs:
				if seq in self.latex_ops:
					doc_ids.extend([Encoder.tokenizer.TokenToId(seq)])
				else:
					doc_ids.extend(Encoder.tokenizer.tokenize(seq))

			return doc_ids

		combined_ids = []
		for data in json.loads(json_line)['data']:
			if "input" in data and data["input"] != "":
				prompt = "### Instruction:\n{}\n\n### Response:\n".format(
                	data["prompt"] + data["input"])
				#prompt = "{}\n{}\n".format(data["prompt"], data["input"])
			else:
				prompt = "### Instruction:\n{}\n\n### Response:\n".format(data["prompt"])
				#prompt = "{}\n".format(data["prompt"])

			input_ids = []
			if "[MASK]" in prompt:
				try:
					assert len(prompt.split('[MASK]')) == len(data['response']['Bert']) + 1
				except Exception as ex:
					print(data, ex)
					exit(0)
				prompt_ids = [_encode(p) for p in prompt.split("[MASK]")]
				for i, ids in enumerate(prompt_ids[:-1]):
					input_ids.extend(prompt_ids[i])
					input_ids.append(Encoder.tokenizer.TokenToId('MASK'))
				input_ids.extend(prompt_ids[-1])
			else:
				input_ids.extend(_encode(prompt))

			eop = [Encoder.tokenizer.TokenToId("eop")]
			sop = [Encoder.tokenizer.TokenToId("sop")]

			if 'response' in data:
				response_ids = []
				if isinstance(data['response'], list):
					if isinstance(data['response'][0], str):
						response_ids.extend(_encode(data['response'][0]))
					elif isinstance(data['response'][0], list):
						assert isinstance(data['response'][0][0], str) 
						response_ids.extend(_encode(data['response'][0][0]))
					else:
						assert False
				elif isinstance(data['response'], str):
					response_ids.extend(_encode(data['response']))
				else:
					if 'Bert' in data['response'] and len(data["response"]["Bert"]) > 0:
						bert_ids = [sop + _encode(b) + eop for b in data["response"]["Bert"]]
						for ids in bert_ids:
							response_ids.extend(ids)
					else:
						bert_ids = []

					if 'GPT' in data['response'] and len(data["response"]["GPT"]) > 0:
						if isinstance(data["response"]["GPT"], list):
							gpt_ids = [_encode(g) for g in data["response"]["GPT"]]
						else:
							gpt_ids = [_encode(data["response"]["GPT"])]

						for ids in gpt_ids:
							response_ids.extend(ids)
					else:
						gpt_ids = []

				if len(input_ids) > 0 and len(response_ids) > 0:
					combined_ids.append(input_ids \
						+ [Encoder.tokenizer.TokenToId('gMASK')] \
						+ response_ids \
						+ [Encoder.tokenizer.TokenToId('eod')])
			else:
				if len(input_ids) > 0:
					combined_ids.append(input_ids + [Encoder.tokenizer.TokenToId('eod')])

		if self.args.concat_sequence:
			return {self.args.json_keys[0]: combined_ids}, len(json_line)
		else:
			length_per_samples = self.args.length_per_sample
			if len(combined_ids) < length_per_samples:
				padded_ids = combined_ids.append([Encoder.tokenizer.TokenToId('[pad]')] * (length_per_samples - len(combined_ids)))
			else:
				padded_ids = [] 
			return {self.args.json_keys[0]: [padded_ids]}, len(json_line)

	def concat_sequence(self, encoded_docs):
		"""
		Combine short sequences into one long sequence, maintain
		the length of long sequence shorter than args.length_per_samples
		"""
		long_docs = []
		length_per_sample = self.args.length_per_sample

		eod = [Encoder.tokenizer.TokenToId("eod")]
		pad = [Encoder.tokenizer.TokenToId('[pad]')]
		gmask = Encoder.tokenizer.TokenToId('gMASK')

		num_exceed = 0
		num_proced = 0
		for key in self.args.json_keys:
			concat_doc = []
			for content, _ in tqdm(encoded_docs):
				num_proced += 1
				if num_proced % 10000 == 1:
					print(" >>>>>>>>>>>>>>>> num exceed sentence: ", num_exceed)

				for doc in content[key]:
					if isinstance(doc[0], list):
						flatten = []
						for d in doc:
							flatten.extend(d)
						doc = flatten

					if len(doc) > length_per_sample - self.args.reserve_tokens:
						if self.args.reserve_long_doc and gmask not in doc:
							length = length_per_sample - self.args.reserve_tokens - 1
							doc = doc[:-1] # remove eod 
							split_docs = [doc[i:i+length] for i in range(0, len(doc), length)]
							for sd in split_docs:
								if len(sd) < 32:
									continue
								sd = sd + eod + pad * (length_per_sample - (len(sd) + 1))
								long_docs.append(({key: [sd]}, len(sd)))
						num_exceed += 1
						continue

					if len(doc) + len(concat_doc) > length_per_sample - self.args.reserve_tokens:
						if len(doc) > 32:
							padded_ids = concat_doc + pad * (length_per_sample - len(concat_doc))
							long_docs.append(({key: [padded_ids]}, len(concat_doc)))
						concat_doc = []
					concat_doc.extend(doc)

			padded_ids = concat_doc + pad * (length_per_sample - len(concat_doc))
			long_docs.append(({key: [padded_ids]}, len(concat_doc)))

		print(" >>>>>>>>>>>>>>>> num exceed sentence: ", num_exceed)
		return long_docs

	def decode(self, ids):
		return self.text_postprocess("".join([Encoder.tokenizer.detokenize(id) for id in ids]))

	def text_preprocess(self, text):
		text = text.replace("\n", "<n>")
		text = text.replace("\t", "<t>")
		return text

	def text_postprocess(self, text):
		text = text.replace("<n>", "\n")
		text = text.replace("<t>", "\t")
		return text


def get_args():
	parser = argparse.ArgumentParser()
	group = parser.add_argument_group(title='input data')
	group.add_argument('--input', type=str,
					   help='Path to input JSON')
	group.add_argument('--datasets', nargs='+', default=None,
					   help='Paths to one or more input datasets to merge')
	group.add_argument('--json-keys', nargs='+', default=['text'],
					   help='space separate listed of keys to extract from json')
	group.add_argument('--split-sentences', action='store_true',
					   help='Split documents into sentences.')
	group.add_argument('--keep-newlines', action='store_true',
					   help='Keep newlines between sentences when splitting.')

	group = parser.add_argument_group(title='tokenizer')
	group.add_argument('--tokenizer-type', type=str, required=True,
					   choices=['BertWordPieceLowerCase',
					   			'BertWordPieceCase',
								'GPT2BPETokenizer', 
								'IceTokenizer',
								'PretrainedFromHF', 
								'CspTokenizer'],
					   help='What type of tokenizer to use.')
	group.add_argument('--vocab-file', type=str, default=None,
					   help='Path to the vocab file')
	group.add_argument('--merge-file', type=str, default=None,
					   help='Path to the BPE merge file (if necessary).')
	group.add_argument('--append-eod', action='store_true',
					   help='Append an <eod> token to the end of a document.')
	group.add_argument("--tokenizer-name-or-path", type=str, default=None,
					   help="Name or path of the huggingface tokenizer.")
	group.add_argument('--make-vocab-size-divisible-by', type=int, default=128,
					   help='Pad the vocab size to be divisible by this value.'
							'This is added for computational efficieny reasons.')
	group.add_argument('--pad-vocab-size-to', type=int, default=None,
					   help='Pad the vocab size to be divisible by this value.'
							'Value of the size of the vocabulary of the tokenizer to reach. This value must be greater than'
							' the initial size of the tokenizer. If this argument is used the value of '
							'`make-vocab-size-divisible-by` will be ignored.')

	group = parser.add_argument_group(title='output data')
	group.add_argument('--output-prefix', type=str, required=True,
					   help='Path to binary output file without suffix')
	group.add_argument('--dataset-impl', type=str, default='mmap',
					   choices=['lazy', 'cached', 'mmap'])

	group = parser.add_argument_group(title='runtime')
	group.add_argument('--workers', type=int, default=1,
					   help='Number of worker processes to launch')
	group.add_argument('--log-interval', type=int, default=100,
					   help='Interval between progress updates')
	group.add_argument('--length-per-sample', type=int, default=1024,
					   help='Number of tokens for each training sample')
	group.add_argument('--store-int32', action='store_true', default=False,
					   help='Store tokens in np.int32 dtype, otherwise will use np.unit16 if vocab_size < 65500')
	group.add_argument('--encode-instruction', action='store_true', default=False,
					   help='Store tokens in np.int32 dtype, otherwise will use np.unit16 if vocab_size < 65500')
	group.add_argument('--encode-multitask', action='store_true', default=False,
					   help='Encode bert loss and gpt loss multitask data. Which would involve [MASK] token in instruction')
	group.add_argument('--concat-sequence', action='store_true', default=False,
					   help='Concat short sequence into one long sequence')
	group.add_argument('--reserve-tokens', default=0, type=int,
					   help='Reserve serve blank tokens at the end of concated sequence')
	group.add_argument('--reserve-long-doc', action='store_true', default=False, 
					   help='Reserve long sequence whose length is exceed length-per-sample, These long sequence will be splited into short sentences')
	group.add_argument('--simplify-latex', action='store_true', default=False, 
					   help='Remove redundant brackets in latex format')
	args = parser.parse_args()
	args.keep_empty = False

	if args.tokenizer_type.lower().startswith('bert'):
		if not args.split_sentences:
			print("Bert tokenizer detected, are you sure you don't want to split sentences?")

	# some default/dummy values for the tokenizer
	args.rank = 0
	args.tensor_model_parallel_size = 1
	args.vocab_extra_ids = 0

	return args

def test():
	args = get_args()
	startup_start = time.time()

	print("Opening", args.input)
	#fin = open(args.input, 'r', encoding='utf-8')

	if nltk_available and args.split_sentences:
		nltk.download("punkt", quiet=True)

	encoder = Encoder(args)
	encoder.initializer()
	tokenizer = build_tokenizer(args) 
	#out = open("id_map", 'w')
	#for symb in latex_operators().keys():
	#	target_id = tokenizer.TokenToId(symb)
	#	print(symb, tokenizer.tokenize(symb), tokenizer.detokenize(tokenizer.tokenize(symb)))
	#	out.write(json.dumps({"target":target_id, "source":tokenizer.tokenize(symb)}))
	#	out.write("\n")
	#out.close()

	#exit(0)

	#pool = multiprocessing.Pool(args.workers, initializer=encoder.initializer)
	#encode_docs = pool.imap(encoder.encode_multitask_data, fin, 200)

	collator = GLMPreprocessor(
		eod_id=tokenizer.TokenToId("eod"),
		mask_id=tokenizer.TokenToId("MASK"),
		gmask_id=tokenizer.TokenToId("gMASK"),
		sop_id=tokenizer.TokenToId("sop"),
		eop_id=tokenizer.TokenToId("eop"),
		max_seq_length=2048,
		aggregated_samples_per_sequence=1,
		gpt_prob=1.0,
		short_seq_prob=0.02,
		single_span_prob=0.02,
		mask_ratio=0.15,
		average_block_length=3,
		min_gmask_ratio=0.2,
		relative_pos_encoding=False,
		no_2d_encoding=True,
		aggregate_gpt_sample=False,
		adaptive_multitask_encoding=False,
		adaptive_multitask_encoding_length=5.0,
		unified_multitask_encoding=False,
		rank=0,
		device_num=1,
		tokenizer = tokenizer,
	)

	with open(args.input, 'r') as fid:
		nbytes = fid.seek(0, 2)
		flen = fid.tell() // 4 
	bin = np.memmap(args.input, dtype=np.int32, shape=(flen // args.length_per_sample, args.length_per_sample))

	for idx in range(len(bin)): 
		print(Encoder.tokenizer.detokenize(bin[idx].tolist()))
	#encode_docs = [doc for doc in encode_docs]
	#print("Before concat encoded docs ", len(encode_docs))
	#encode_docs = encoder.concat_sequence(encode_docs)
	#print("Finish concat encoded docs ", len(encode_docs))
	#count = 0
	#for doc, bytes in encode_docs:
	#	for key, sentences in doc.items():
	#		for idx, sentence in enumerate(sentences):
	#			tokens, targets, loss_masks, position_ids, division, _ = collator.get_custom_multitask_data(np.array(sentence), idx)
	#			#np.set_printoptions(threshold=1e6)
	#			print(Encoder.tokenizer.detokenize(targets.tolist()).replace("[<br>]", "\n"))
	#			count += 1
	#			if count == 1000:
	#				exit(0)

def main():
	args = get_args()
	startup_start = time.time()

	print("Opening", args.input)
	fin = open(args.input, 'r', encoding='utf-8')

	if nltk_available and args.split_sentences:
		nltk.download("punkt", quiet=True)

	encoder = Encoder(args)
	#tokenizer = build_tokenizer(args)
	pool = multiprocessing.Pool(args.workers, initializer=encoder.initializer)
	if args.encode_instruction:
		encoded_docs = pool.imap(encoder.encode_instruction_data, fin, 200)
	elif args.encode_multitask:
		encoded_docs = pool.imap(encoder.encode_multitask_data, fin, 200)
	else:
		encoded_docs = pool.imap(encoder.encode, fin, 200)

	encoder.initializer()
	tokenizer = encoder.tokenizer 
	if args.concat_sequence:	
		encoded_docs = encoder.concat_sequence(encoded_docs)
		print("Number of docs after concate: {}".format(len(encoded_docs)))

	level = "document"
	if args.split_sentences:
		level = "sentence"

	print(f"Vocab size: {tokenizer.vocab_size}")
	print(f"Output prefix: {args.output_prefix}")
	output_bin_files = {}
	output_idx_files = {}
	builders = {}
	for key in args.json_keys:
		output_bin_files[key] = "{}_{}_{}.bin".format(args.output_prefix,
													key, level)
		output_idx_files[key] = "{}_{}_{}.idx".format(args.output_prefix,
													key, level)
		dtype = np.int32 if args.store_int32 else best_fitting_dtype(tokenizer.vocab_size)
		builders[key] = indexed_dataset.make_builder(output_bin_files[key],
													 impl=args.dataset_impl,
													 dtype=dtype)
													 #dtype=best_fitting_dtype(tokenizer.vocab_size))
		print(" >>>>>>>> Data type check: {}".format(dtype))

	startup_end = time.time()
	proc_start = time.time()
	total_bytes_processed = 0
	print("Time to startup:", startup_end - startup_start)

	for i, (doc, bytes_processed) in enumerate(encoded_docs, start=1):
		total_bytes_processed += bytes_processed
		for key, sentences in doc.items():
			if len(sentences) == 0:
				continue
			for sentence in sentences:
				builders[key].add_item(torch.IntTensor(sentence))
			builders[key].end_document()
		if i % args.log_interval == 0:
			current = time.time()
			elapsed = current - proc_start
			mbs = total_bytes_processed/elapsed/1024/1024
			print(f"Processed {i} documents",
				f"({i/elapsed} docs/s, {mbs} MB/s).",
				file=sys.stderr)

	for key in args.json_keys:
		builders[key].finalize(output_idx_files[key])

if __name__ == '__main__':
	main()
	#test()
