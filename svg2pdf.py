#!/usr/bin/python
#c.f. http://empitsu.hatenablog.com/entry/2013/02/06/205135

import os, sys
import re
import tempfile
from xml.etree.ElementTree import *

svg_ns      = 'http://www.w3.org/2000/svg'
inkscape_ns = 'http://www.inkscape.org/namespaces/inkscape'
sodipodi_ns = 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'

gs_exe = 'gs'
is_exe = 'inkscape'
bg_keyword = 'background'
pi_keyword = 'pages'      

argv = sys.argv
argc = len(argv)
if(argc < 2):
    print 'Usage: svg2pdf.py hoge.svg'
    quit()

path = argv[1]
base, ext = os.path.splitext(path)

tree = parse(path)
pdfs = ''
fg_list = [] # foreground layers
bg_list = [] # background layers
pi_list = [] # page-indicators

# finding page indicators
for text in tree.findall('.//{%s}text' % svg_ns):
    if text.get('id').find(pi_keyword) >= 0:
        pi_list.append(text)

# setting all foreground layers hidden and all background visible
for layer in tree.findall('.//{%s}g' % svg_ns):
    if re.search(r'^layer[0-9]+$', layer.get('id')) == None:
        continue
    
    if layer.get('{%s}label' % inkscape_ns).find(bg_keyword) >= 0:
        layer.set('style', 'display:inline')
        bg_list.append(layer)
    else:
        layer.set('style', 'display:none')
        fg_list.append(layer)

# create a temporary pdf file for each foreground layerfor i, layer in enumerate(fg_list):
    layer.set('style', 'display:inline')

    for pi in pi_list:
        pi[0].text = '%d / %d' % (i+1, len(fg_list))
    
    temp_svg = tempfile.mkstemp(suffix='.svg')
    tree.write(temp_svg[1], 'UTF-8')
    
    temp_pdf = tempfile.mkstemp(suffix='.pdf')
    os.close(temp_pdf[0])
    cmd = '%s -C -f \"%s\" -A %s' \
        % (is_exe, temp_svg[1], temp_pdf[1])
    print cmd
    os.system(cmd)
    pdfs += '%s ' % temp_pdf[1]

    os.close(temp_svg[0])
    os.remove(temp_svg[1])
    
    layer.set('style', 'display:none')

# bind all the pdf files into one
cmd = '%s -dNOPAUSE -sDEVICE=pdfwrite ' % gs_exe \
    + '-dAutoFilterColorImages=false ' \
    + '-dColorImageFilter=/FlateEncode ' \
    + '-sOUTPUTFILE=%s.pdf -dBATCH %s' \
    % (base, pdfs)
print cmd
os.system(cmd)

# delete all the temporary pdf files
for temp_pdf_path in pdfs.split():
    os.remove(temp_pdf_path)
