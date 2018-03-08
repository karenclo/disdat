"""
Pipe for getting basic alignment statistics for a sequenced subject genome.

@author: twong
@copyright: Human Longevity, Inc. 2017
@license: Apache 2.0

To run this example at the command line (assuming that your current working
directory is $DISDAT_ROOT):

1. Create toy.csv from examples/data/toy.csv.template by substituting in
the path for $DISDAT_ROOT.
2. `dsdt add toy-sam toy.csv`
3. `dsdt cat toy-sam`. You should see that Disdat has 'localized' the toy
SAM file within the local Disdat context.
4. `export PYTHONPATH=$DISDAT_ROOT/examples:$PYTHONPATH` to add the example
modules to the Python module search path.
5. `dsdt apply toy-sam toy-flagstat pipelines.flagstat.Flagstat`.
6. `dsdt cat toy-flagstat`. You should see a Disdat localized flagstat file
corresponding to the results of running `samtools flagstat` on the toy SAM
file.
"""

# Using print as a function makes it easier to switch between printing
# during development and using logging.{debug, info, ...} in production.
from __future__ import absolute_import, division, print_function, unicode_literals

# Built-in imports
import logging
import subprocess

# Third-party imports
import disdat.pipe as pipe
from disdat.utility.which import which

_logger = logging.getLogger(__name__)


class Flagstat(pipe.PipeTask):
    '''A pipe to get basic alignment statistics for a sequenced subject
    genome using :code:`samtools`.
    '''
    INPUT_SAMPLE_KEY = 'sample_key'
    INPUT_BAM_KEY = 'bam'

    OUTPUT_SAMPLE_KEY = 'sample_key'
    OUTPUT_STAT_KEY = 'stats'

    flagstat_command = ['samtools', 'flagstat']

    def __init__(self, *args, **kwargs):
        if which(self.flagstat_command[0]) is None:
            raise OSError('Unable to find executable \'{}\''.format(self.flagstat_command[0]))
        super(Flagstat, self).__init__(*args, **kwargs)

    def pipe_run(self, pipeline_input=None):
        ''' Run :code:`samtools` to collect basic alignment statistics for a
        sequenced subject genome. We create a flagstat file in the output
        bundle for the BAM/SAM file in the input.

        :param pipeline_input: A dict-like containing the subject sample key
        :return: A dict-like containing the subject sample key and the path
            to a file containing the output of :code:`samtools flagstat`
        '''
        # We exercise an abundance of caution in this example by validating the
        # pipeline input
        if pipeline_input is None:
            raise ValueError('Missing pipeline input bundle')
        if pipeline_input.shape[0] != 1:
            raise ValueError('Got an invalid input bundle: Expected shape (1, *), got {}'.format(pipeline_input.shape))
        input_row = pipeline_input.iloc[0]
        _logger.debug('Input is {}'.format(input_row.values))
        sample_key = input_row[self.INPUT_SAMPLE_KEY]
        bam = input_row[self.INPUT_BAM_KEY]
        # Create an output file in the Disdat local file space to save the
        # output from samtools flagstat
        target_filename = '{}.stat'.format(sample_key)
        target = self.create_output_file(target_filename)
        command = self.flagstat_command + [bam]
        _logger.info('Calling \'{}\' on sample {}'.format(' '.join(command), sample_key))
        # Call samtools as an external subprocess, and capture the output in the
        # output file we created in the Disdat local file space
        with target.open('w') as target_file:
            subprocess.check_call(command, stdout=target_file)
        # Return the dict. Disdat will write this into a bundle as a dataframe.
        return {
            self.OUTPUT_SAMPLE_KEY: [sample_key],
            self.OUTPUT_STAT_KEY: [target],
        }
