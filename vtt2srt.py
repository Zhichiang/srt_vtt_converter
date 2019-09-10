import argparse
import codecs
import sys
import os

import vtttosrt


def _get_args():
    parser = argparse.ArgumentParser(description='A useful tool that \
                convert srt subtitle files to vtt subtitle files.')
    parser.add_argument('-o', '--output-dir', default=os.getcwd(),
                        help='output directory (default: current directory)')
    parser.add_argument('-f', '--force', action="store_true",
                        help='force overwrite exist SRT files')
    parser.add_argument('files', nargs='*',
                        help='paths of ASS/SSA files (default: all on current directory)')
    return parser.parse_args()


def _check_chardet():
    """Import chardet or exit."""
    global chardet
    try:
        import chardet
    except ImportError:
        print('Error: module "chardet" not found.\nPlease install it ' + \
              '(pip install chardet) or specify a encoding (-e utf-8).',
              file=sys.stderr)
        sys.exit(1)


def _files_on_cwd():
    """Return all ASS/SSA file on current working directory. """
    files = []
    for file in os.listdir(os.getcwd()):
        if file.startswith('.'):
            continue
        if file.endswith('.vtt'):
            files.append(file)
    return files


def _detect_charset(file):
    """Try detect the charset of file, return the name of charset or exit."""
    bytes = file.read(4096)
    file.seek(0)
    c = chardet.detect(bytes)
    if c['confidence'] < 0.3:
        print('Error: unknown file encoding, ', file=sys.stderr)
        sys.exit(1)
    elif c['confidence'] < 0.6:
        print('Warning: uncertain file encoding, ', file=sys.stderr)
    if c['encoding'] == 'GB2312':
        return 'GB18030'
    return c['encoding']


CODECS_BOM = {
    'utf-16': codecs.BOM_UTF16,
    'utf-16-le': codecs.BOM_UTF16_LE,
    'utf-16-be': codecs.BOM_UTF16_BE,
    'utf-32': codecs.BOM_UTF16,
    'utf-32-le': codecs.BOM_UTF32_LE,
    'utf-32-be': codecs.BOM_UTF32_BE,
}


def get_bom(codec):
    """Return the BOM of UTF-16/32 or empty str."""
    if codec.name in CODECS_BOM:
        return CODECS_BOM[codec.name]
    else:
        return b''


def _combine_output_file_path(in_files, output_dir):
    files = []
    for file in in_files:
        name = os.path.splitext(os.path.basename(file))[0] + '.srt'
        path = os.path.join(output_dir, name)
        files.append((file, path))
    return files


def _convert_files(files, args):
    sum = len(files)
    done = 0
    fail = 0
    ignore = 0
    print("Found {} file(s), converting...".format(sum))
    for in_path, out_path in _combine_output_file_path(files, args.output_dir):
        print("\t({:02d}/{:02d}) is converting... ".format(
            done + fail + ignore + 1, sum), end='')
        if not args.force and os.path.exists(out_path):
            print('[ignore] (VTT exists)')
            ignore += 1
            continue
        try:
            with open(in_path, 'rb') as in_file:
                in_codec = codecs.lookup(_detect_charset(in_file))
                out_codec = in_codec

                out_str = vtttosrt.convert(in_codec.streamreader(in_file))

            with open(out_path, 'wb') as out_file:
                out_file.write(get_bom(out_codec))
                out_file.write(out_codec.encode(out_str)[0])
            done += 1
            print('[done]')

        except (UnicodeDecodeError, UnicodeEncodeError, LookupError) as e:
            print('[fail] (codec error)')
            print(e, file=sys.stderr)
            fail += 1
        except ValueError as e:
            print('[fail] (irregular format)')
            print(e, file=sys.stderr)
            fail += 1
        except IOError as e:
            print('[fail] (IO error)')
            print(e, file=sys.stderr)
            fail += 1

    print("All done:\n\t{} success, {} ignore, {} fail." \
          .format(done, ignore, sum - done - ignore))


def main():
    args = _get_args()
    _check_chardet()

    files = args.files
    if not files:
        files = _files_on_cwd()
    if not files:
        print('srt file no found.', file=sys.stderr)
        sys.exit(1)

    _convert_files(files, args)


if __name__ == '__main__':
    main()
