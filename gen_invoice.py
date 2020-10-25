import sys, os, datetime, json
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from rlextra.rml2pdf import rml2pdf
import jsondict
from rlextra.radxml.html_cleaner import cleanBlocks
from rlextra.radxml.xhtml2rml import xhtml2rml
import preppy

def bb2rml(text):
	return preppy.SafeString(xhtml2rml(cleanBlocks(bbcode.render_html(text)),ulStyle="normal_ul", olStyle="normal_ol"))

def generate_pdf(json_file_name, options):
	data = json.load(open(json_file_name))

	here = os.path.abspath(os.path.dirname('__file__'))
	output = os.path.abspath(options.output)
	if not os.path.isdir(output):
		os.makedirs(output,0o755)
		
	data = jsondict.condJSONSafe(data)	
	ns = dict(data=data, bb2rml=bb2rml, format="long" if options.longformat else "short")		
	ns['RML_DIR'] = os.getcwd()
	FONT_DIR = ns['FONT_DIR'] = os.path.join(ns['RML_DIR'], 'fonts')
	
	for fn in os.listdir(FONT_DIR):
		print("font name:"+fn)
		pdfmetrics.registerFont(TTFont(os.path.splitext(fn)[0],fn))
	
	ns['RSRC_DIR'] = os.path.join(ns['RML_DIR'], 'resources')
	template = preppy.getModule('PythonInvoice.prep')
	rmlText = template.getOutput(ns, quoteFunc=preppy.stdQuote)
	file_name_root = os.path.join(output,os.path.splitext(os.path.basename(json_file_name))[0]) 

	if options.saverml:
		rml_file_name = file_name_root + '.rml'
		open(rml_file_name, 'w').write(rmlText)
	pdf_file_name = file_name_root + '.pdf'
	rml2pdf.go(rmlText, outputFileName=pdf_file_name)
	print('saved %s' % pdf_file_name)

if __name__=='__main__':
	from optparse import OptionParser
	usage = "usage: gen_invoice.py [--long] myfile.json"
	parser = OptionParser(usage=usage)
	parser.add_option("-l", "--long",
					  action="store_true", dest="longformat", default=False,
					  help="Do long profile (rather than short)")
	parser.add_option("-r","--rml",
					  action="store_true", dest="saverml", default=False,
					  help="save a copy of the generated rml")
	parser.add_option("-s","--showb",
					  action="store_true", dest="showBoundary", default=False,
					  help="turn on global showBoundary flag")
	parser.add_option("-o", "--output",
					  action="store", dest="output", default='output',
					  help="where to store result")

	options, args = parser.parse_args()

	if len(args) != 1:
		print(parser.usage)
	else:
		filename = args[0]
		generate_pdf(filename, options) 