#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import quantipy as qp
from quantipy.core.tools.qp_decorators import *

from collections import OrderedDict
import json

class Audit(object):
	"""
	Container for qp.DataSet instances, which get compared.
	"""
	# ------------------------------------------------------------------------
	# Conventions
	# ------------------------------------------------------------------------

	def __init__(self, datasets, path=None, dimensions_comp=True):
		self.datasets = []
		self.path = path
		self._dimensions_comp = dimensions_comp
		self.ds_names = []
		self.all_incl_vars = []
		self.unpaired_vars = None
		self.add_datasets(datasets)


	@verify(is_str='ds')
	@modify(to_list='ds')
	def __getitem__(self, ds):
		not_incl = [d for d in ds if not
						any(dataset.name == d for dataset in self.datasets)]
		if not_incl:
			raise ValueError('{} is not included.'.format(not_incl))
		datasets = [d for d in self.datasets if d.name in ds]
		return datasets[0] if len(datasets) == 1 else datasets

	# ------------------------------------------------------------------------
	# file i/o
	# ------------------------------------------------------------------------

	def _load_ds(self, name):
		path_json = '{}/{}.json'.format(self.path, name)
		path_csv = '{}/{}.csv'.format(self.path, name)
		dataset = qp.DataSet(name, self._dimensions_comp)
		dataset.set_verbose_infomsg(False)
		dataset.read_quantipy(path_json, path_csv)
		return dataset


	@modify(to_list='datasets')
	def add_datasets(self, datasets):
		"""
		Add DataSet instances to the Audit container.

		Parameters
		----------
		datasets: qp.DataSet/ str, list of qp.DataSet/ str

		Returns
		-------
		None
		"""
		for ds in datasets:
			if isinstance(ds, qp.DataSet):
				if not ds.name in self.ds_names:
					self.datasets.append(ds)
			elif not self.path:
				msg = 'If elements in datasets are str, a path must be provided: {}'
				raise ValueError(msg.format(ds))
			else:
				dataset = self._load_ds(ds)
				if not ds in self.ds_names:
					self.datasets.append(dataset)
				else:
					raise ValueError('{} is already in Audit.'.format(ds.name))
			self._get_ds_names()
		self.all_incl_vars = self._all_incl_vars()
		return None

	def _get_ds_names(self):
		for ds in self.datasets:
			if not ds.name in self.ds_names:
				self.ds_names.append(ds.name)
		return None

	def add_path(self, path):
		"""
		Define the path attribute.
		"""
		self.path = path
		return None

	@modify(to_list='names')
	def save(self, names=None, suffix='_audit'):
		"""
		Save all included DataSet instances.
		"""
		if not names:
			names = self.ds_names
		elif not all(n in self.ds_names for n in names):
			not_incl = [n not in self.ds_names for n in names]
			raise ValueError('{} is not included.'.format(not_incl))
		path = self.path
		for n in names:
			ds = self[n]
			if not path: path = ds.path
			path = '../' if path == '/' else path
			path_json = '{}/{}{}.json'.format(path, n, suffix)
			path_csv = '{}/{}{}.csv'.format(path, n, suffix)
			ds.write_quantipy(path_json, path_csv)
			print 'Created:\n\t{}\n\t{}'.format(path_json, path_csv)
		return None

	# ------------------------------------------------------------------------
	# update
	# ------------------------------------------------------------------------

	def _update(self):
		self.all_incl_vars = self._all_incl_vars()
		self.mismatches()
		return None

	# ------------------------------------------------------------------------
	# validate
	# ------------------------------------------------------------------------

	def validate_all(self, spss_limits=False):
		"""
		Runs validate for included DataSets and reports broken instance names.

		Parameters
		----------
		spss_limits: bool, default False
			Define if spss_limits should be tested or not.

		Returns
		-------
		inconsistent: list of str
			Names of inconsistent DataSet instances.
		"""
		inconsistent = []
		for ds in self.datasets:
			if not ds.validate(spss_limits, False) is None:
				inconsistent.append(ds.name)
		if not inconsistent:
			print 'No issues found in the datasets!'
		return inconsistent

	# ------------------------------------------------------------------------
	# mismatches
	# ------------------------------------------------------------------------

	def mismatches(self):
		"""
		Reports variables that are not included in all DataSets.

		Returns
		-------
		unpaired: pd.DataFrame
		"""
		var_map = self._misspelling_map()
		unpaired = []

		for var in self.all_incl_vars:
			header = OrderedDict()
			for name in self.ds_names:
				if var in var_map[var.lower()].get(name, []):
					header[name] = ''
				else:
					header[name] = []
					for v in self.all_incl_vars:
						if v == var:
							continue
						elif var.lower() == v.lower():
							header[name] = var_map[v.lower()][name]
							break
						elif var.lower() in v.lower() and name in var_map[v.lower()]:
							header[name].extend(var_map[v.lower()][name])
					if not header[name]:
						header[name] = 'x'
			df = pd.DataFrame([header], index=[var])
			if not all(v == '' for v in df.values.tolist()[0]):
				unpaired.append(df)
		if unpaired:
			unpaired = pd.concat(unpaired, axis=0)
			self.unpaired_vars = unpaired
			return unpaired
		else:
			self.unpaired_vars = None
			print 'No unpaired variables found in the datasets!'
			return None

	def _misspelling_map(self):
		name_map = {}
		for name in self.ds_names:
			for v in self[name].variables():
				low = v.lower()
				if name_map.get(low, {}).get(name):
					name_map[low][name].append(v)
				elif name_map.get(low):
					name_map[low].update({name: [v]})
				else:
					name_map[low] = {name: [v]}
		return name_map

	def _all_incl_vars(self):
		all_included = []
		for ds in self.datasets:
			for v in ds.variables():
				if not v in all_included:
					all_included.append(v)
		return all_included

	@modify(to_list=['datasets', 'ignore'])
	@verify(is_str=['name', 'datasets', 'ignore'])
	def rename_by(self, name, datasets=None, ignore=[]):
		"""
		Take over variable names of a defined DataSet.

		Loops over ``self.unpaired_vars`` and if only one alternative variable
		is included, it is renamed by name of the variable in the master
		DataSet.

		Parameters
		----------
		name: str
			Name of the master DataSet from which the variables names are taken.
		datasets: str/ list of str
			Name(s) of the DataSet(s) for which the variables should be renamed.
			If None, all included DataSets are taken, except of the master
			DataSet.
		ignore: str/ list of str
			Name(s) of variables that will not be renamed.

		Returns
		-------
		None
		"""
		if self.unpaired_vars is None:
			self.mismatches()
		if self.unpaired_vars is None:
			print 'No mismatches detected in included DataSets.'
			return None
		m_ds = self[name]
		if not datasets: datasets = [ds for ds in self.ds_names if not ds == name]
		for ds in datasets:
			for var, incl in self.unpaired_vars[[ds]].iterrows():
				v = incl.values.tolist()[0]
				if isinstance(v, list) and len(v) == 1 and m_ds.var_exists(var):
					self[ds].rename(v[0], var)
		self._update()
		return None

	@modify(to_list='datasets')
	@verify(is_str='datasets')
	def rename_from_mapper(self, datasets=None, mapper={}):
		"""
		Renames variables from mapper for all defined datasets.

		Parameters
		----------
		datasets: str/ list of str
			Name(s) of the DataSet(s) for which the variables should be renamed.
			If None, all included DataSets are taken.
		mapper: dict in form if {str: str}
			The key is renamed into the value.

		Returns
		-------
		None
		"""
		if not isinstance(mapper, dict):
			raise ValueError("'mapper' must be a dict: {str: str}")
		elif not all(isinstance(k, (str, unicode)) and isinstance(v, (str, unicode))
		             for k, v in mapper.items()):
			raise ValueError("'mapper' must be a dict: {str: str}")
		if not datasets: datasets = self.ds_names
		for ds in datasets:
			for k, v in mapper.items():
				if self[ds].var_exists(k):
					self[ds].rename(k, v)
		self._update()
		return None

	@modify(to_list=['datasets', 'ignore'])
	@verify(is_str=['datasets', 'ignore'])
	def remove_mismatches(self, datasets, ignore=[]):
		"""
		Remove variables that are not included in all DataSets.

		Parameters
		----------
		datasets: str/ list of str
			Name(s) of the DataSet(s) for which the variables should be removed.
			If None, all included DataSets are taken.
		ignore: str/ list of str
			Name(s) of variables that will not be removed.

		Returns
		-------
		None
		"""
		if self.unpaired_vars is None:
			self.mismatches()
		if self.unpaired_vars is None:
			print 'No mismatches detected in included DataSets.'
			return None
		if not datasets: datasets = self.ds_names
		for ds in datasets:
			for v in self.unpaired_vars.index.tolist():
				if self[ds].var_exists(v) and not v in ignore:
					self[ds].drop(v)
		print 'Removed unpaired variables from {}.'.format(datasets)
		self._update()
		return None

	# ------------------------------------------------------------------------
	# missing array items
	# ------------------------------------------------------------------------

	def unpaired_array_items(self):
		"""
		Check if included arrays have the same items.
		"""
		arrays = [a for a in self.all_incl_vars
				  if any(d.var_exists(a) and d._is_array(a)
				         for d in self.datasets)]
		arrays = []
		total_ais = OrderedDict()
		for v in self.all_incl_vars:
			for d in self.datasets:
				if d.var_exists(v) and d._is_array(v):
					if not v in arrays: arrays.append(v)
					total_ais[v] = []
					for source in d.sources(v):
						if not source in total_ais[v]:
							total_ais[v].append(source)

		all_df = []
		for a in arrays:
			a_header = OrderedDict()
			items_df = []
			for s in total_ais[a]:
				i_header = OrderedDict()
				for name in self.ds_names:
					if not name in a_header:
						if not self[name].var_exists(a):
							a_header[name] = 'x'
						elif not self[name]._get_type(a) == 'array':
							a_header[name] = self[name]._get_type(a)
						else:
							a_header[name] = ''
					if not any(self[name].var_exists(v) for v in [a, s]):
						i_header[name] = 'x'
					elif not s in self[name].sources(a):
						i_header[name] = 'x'
					else:
						i_header[name] = ''
				i_df = pd.DataFrame([i_header], index=[s])
				if not all(v == '' for v in i_df.values.tolist()[0]):
					items_df.append(i_df)
			a_df = pd.DataFrame([a_header], index=[a])
			if not all(v == '' for v in a_df.values.tolist()[0]):
				all_df.append(a_df)
			if items_df:
				items = pd.concat(items_df, axis=0)
				all_df.append(items)
		return pd.concat(all_df, axis=0)

