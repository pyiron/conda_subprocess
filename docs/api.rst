Interface
=========

Documentation of the classes and functions defined in the :code:`conda_subprocess` package. For an
introduction with runnable examples, see the `README <README.html>`_ and the `demo notebook <demo.html>`_.

The subprocess-style functions (:code:`call`, :code:`check_call`, :code:`check_output`, :code:`run`,
:code:`Popen`) mirror their :code:`subprocess` counterparts and add :code:`prefix_name`/:code:`prefix_path`
keyword arguments to select the target conda environment - see :func:`conda_subprocess.process.Popen` for
details. The :func:`conda_subprocess.decorator.conda` decorator runs a whole Python function in another
conda environment instead.

.. autosummary::
   :toctree: _autosummary
   :template: custom-module-template.rst
   :recursive:

   conda_subprocess