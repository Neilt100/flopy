"""
mflmt module.  Contains the ModflowLmt class. Note that the user can access
the ModflowLmt class as `flopy.modflow.ModflowLmt`.

Additional information for this MODFLOW package can be found at the `Online
MODFLOW Guide
<http://water.usgs.gov/ogw/modflow/MODFLOW-2005-Guide/index.html?lmt.htm>`_.

"""
import os
import sys
from ..pakbase import Package


class ModflowLmt(Package):
    """
    MODFLOW Link-MT3DMS Package Class.

    Parameters
    ----------
    model : model object
        The model object (of type :class:`flopy.modflow.mf.Modflow`) to which
        this package will be added.
    output_file_name : string
        Filename for output file (default is 'mt3d_link.ftl')
    unitnumber : int
        File unit number (default is 24).
    output_file_unit : int
        Output file unit number, pertaining to the file identified
        by output_file_name (default is 54).
    output_file_header : string
        Header for the output file (default is 'extended')
    output_file_format : {'formatted', 'unformatted'}
        Format of the output file (default is 'unformatted')
    package_flows : {'sfr', 'lak', 'uzf'}
        Specifies which package flows should be added to the flow-transport
        link (FTL) file. These values can quickly raise the file size, and
        therefore the user must request there addition to the FTL file.
        Default is not to add these terms to the FTL file by omitting the
        keyword package_flows from the LMT input file.
    extension : string
        Filename extension (default is 'lmt6')
    unitnumber : int
        File unit number (default is 30).

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----
    Parameters are supported in Flopy only when reading in existing models.
    Parameter values are converted to native values in Flopy and the
    connection to "parameters" is thus nonexistent.

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modflow.Modflow()
    >>> lmt = flopy.modflow.ModflowLmt(m, output_file_name='mt3d_linkage.ftl')

    """

    def __init__(self, model, output_file_name='mt3d_link.ftl',
                 output_file_unit=54, output_file_header='extended',
                 output_file_format='unformatted', extension='lmt6',
                 package_flows=[], unitnumber=None, filenames=None):

        # set default unit number of one is not specified
        if unitnumber is None:
            unitnumber = ModflowLmt.defaultunit()

        # set filenames
        if filenames is None:
            filenames = [None]
        elif isinstance(filenames, str):
            filenames = [filenames]

        # Fill namefile items
        name = [ModflowLmt.ftype()]
        units = [unitnumber]
        extra = ['']

        # set package name
        fname = [filenames[0]]

        # Call ancestor's init to set self.parent, extension, name and unit number
        Package.__init__(self, model, extension=extension, name=name,
                         unit_number=units, extra=extra, filenames=fname)

        self.heading = '# {} package for '.format(self.name[0]) + \
                       ' {}, '.format(model.version_types[model.version]) + \
                       'generated by Flopy.'
        self.url = 'lmt.htm'
        self.output_file_name = output_file_name
        self.output_file_unit = output_file_unit
        self.output_file_header = output_file_header
        self.output_file_format = output_file_format
        self.package_flows = package_flows
        self.parent.add_package(self)
        return

    def write_file(self):
        """
        Write the package file.

        Returns
        -------
        None

        """
        f = open(self.fn_path, 'w')
        f.write('{}\n'.format(self.heading))
        f.write('{:20s}\n'.format('OUTPUT_FILE_NAME ' +
                                  self.output_file_name))
        f.write('{:20s} {:10d}\n'.format('OUTPUT_FILE_UNIT ',
                                         self.output_file_unit))
        f.write('{:20s}\n'.format('OUTPUT_FILE_HEADER ' +
                                  self.output_file_header))
        f.write('{:20s}\n'.format('OUTPUT_FILE_FORMAT ' +
                                  self.output_file_format))
        if self.package_flows:  # check that the list is not empty
            # Generate a string to write
            pckgs = ''
            if 'sfr' in [x.lower() for x in self.package_flows]:
                pckgs += 'SFR '
            if 'lak' in [x.lower() for x in self.package_flows]:
                pckgs += 'LAK '
            if 'uzf' in [x.lower() for x in self.package_flows]:
                pckgs += 'UZF '

            line = 'PACKAGE_FLOWS ' + pckgs
            f.write('%s\n' % (line))

        f.close()

    @staticmethod
    def load(f, model, ext_unit_dict=None):
        """
        Load an existing package.

        Parameters
        ----------
        f : filename or file handle
            File to load.
        model : model object
            The model object (of type :class:`flopy.modflow.mf.Modflow`) to
            which this package will be added.
        ext_unit_dict : dictionary, optional
            If the arrays in the file are specified using EXTERNAL,
            or older style array control records, then `f` should be a file
            handle.  In this case ext_unit_dict is required, which can be
            constructed using the function
            :class:`flopy.utils.mfreadnam.parsenamefile`.

        Returns
        -------
        lmt : ModflowLmt object
            ModflowLmt object.

        Examples
        --------

        >>> import flopy
        >>> m = flopy.modflow.Modflow()
        >>> lmt = flopy.modflow.ModflowGhb.load('test.lmt', m)

        """

        if model.verbose:
            sys.stdout.write('loading lmt package file...\n')

        # set default values
        prefix = os.path.basename(f)
        prefix = prefix[:prefix.rfind('.')]
        output_file_name = prefix + '.ftl'
        output_file_unit = 333
        output_file_header = 'standard'
        output_file_format = 'unformatted'
        package_flows = []

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        for line in f:
            if line[0] == '#':
                continue
            t = line.strip().split()
            if len(t) < 2:
                continue
            if t[0].lower() == 'output_file_name':
                output_file_name = t[1]
            elif t[0].lower() == 'output_file_unit':
                output_file_unit = int(t[1])
            elif t[0].lower() == 'output_file_header':
                output_file_header = t[1]
            elif t[0].lower() == 'output_file_format':
                output_file_format = t[1]
            elif t[0].lower() == 'package_flows':
                # Multiple entries can follow 'package_flows'
                if len(t) > 1:
                    for i in range(1, len(t)):
                        package_flows.append(t[i])


        # determine specified unit number
        unitnumber = None
        filenames = [None]
        if ext_unit_dict is not None:
            unitnumber, filenames[0] = \
                model.get_ext_dict_attr(ext_unit_dict,
                                        filetype=ModflowLmt.ftype())

        lmt = ModflowLmt(model, output_file_name=output_file_name,
                         output_file_unit=output_file_unit,
                         output_file_header=output_file_header,
                         output_file_format=output_file_format,
                         package_flows=package_flows,
                         unitnumber=unitnumber,
                         filenames=filenames)
        return lmt

    @staticmethod
    def ftype():
        return 'LMT6'

    @staticmethod
    def defaultunit():
        return 30
