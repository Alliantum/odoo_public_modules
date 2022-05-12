import werkzeug
import pyzint
from odoo import http
from odoo.addons.web.controllers.main import ReportController


# This is the extra list of available symbols that you can pass to Odoo
# Tbarcode 7 codes
# BARCODE_CODE11
# BARCODE_C25MATRIX
# BARCODE_C25INTER
# BARCODE_C25IATA
# BARCODE_C25LOGIC
# BARCODE_C25IND
# BARCODE_CODE39
# BARCODE_EXCODE39
# BARCODE_EANX
# BARCODE_EANX_CHK
# BARCODE_EAN128
# BARCODE_CODABAR
# BARCODE_CODE128
# BARCODE_DPLEIT
# BARCODE_DPIDENT
# BARCODE_CODE16K
# BARCODE_CODE49
# BARCODE_CODE93
# BARCODE_FLAT
# BARCODE_RSS14
# BARCODE_RSS_LTD
# BARCODE_RSS_EXP
# BARCODE_TELEPEN
# BARCODE_UPCA
# BARCODE_UPCA_CHK
# BARCODE_UPCE
# BARCODE_UPCE_CHK
# BARCODE_POSTNET
# BARCODE_MSI_PLESSEY
# BARCODE_FIM
# BARCODE_LOGMARS
# BARCODE_PHARMA
# BARCODE_PZN
# BARCODE_PHARMA_TWO
# BARCODE_PDF417
# BARCODE_PDF417TRUNC
# BARCODE_MAXICODE
# BARCODE_QRCODE
# BARCODE_CODE128B
# BARCODE_AUSPOST
# BARCODE_AUSREPLY
# BARCODE_AUSROUTE
# BARCODE_AUSREDIRECT
# BARCODE_ISBNX
# BARCODE_RM4SCC
# BARCODE_DATAMATRIX
# BARCODE_EAN14
# BARCODE_VIN
# BARCODE_CODABLOCKF
# BARCODE_NVE18
# BARCODE_JAPANPOST
# BARCODE_KOREAPOST
# BARCODE_RSS14STACK
# BARCODE_RSS14STACK_OMNI
# BARCODE_RSS_EXPSTACK
# BARCODE_PLANET
# BARCODE_MICROPDF417
# BARCODE_ONECODE
# BARCODE_PLESSEY

# Tbarcode 8 codes
# BARCODE_TELEPEN_NUM
# BARCODE_ITF14
# BARCODE_KIX
# BARCODE_AZTEC
# BARCODE_DAFT
# BARCODE_MICROQR

# Tbarcode 9 codes
# BARCODE_HIBC_128
# BARCODE_HIBC_39
# BARCODE_HIBC_DM
# BARCODE_HIBC_QR
# BARCODE_HIBC_PDF
# BARCODE_HIBC_MICPDF
# BARCODE_HIBC_BLOCKF
# BARCODE_HIBC_AZTEC

# Tbarcode 10 codes
# BARCODE_DOTCODE
# BARCODE_HANXIN

# Tbarcode 11 codes
# BARCODE_MAILMARK

# Zint specific
# BARCODE_AZRUNE
# BARCODE_CODE32
# BARCODE_EANX_CC
# BARCODE_EAN128_CC
# BARCODE_RSS14_CC
# BARCODE_RSS_LTD_CC
# BARCODE_RSS_EXP_CC
# BARCODE_UPCA_CC
# BARCODE_UPCE_CC
# BARCODE_RSS14STACK_CC
# BARCODE_RSS14_OMNI_CC
# BARCODE_RSS_EXPSTACK_CC
# BARCODE_CHANNEL
# BARCODE_CODEONE
# BARCODE_GRIDMATRIX
# BARCODE_UPNQR
# BARCODE_ULTRA
# BARCODE_RMQR


class ReportControllerExtraBarcodes(ReportController):

    @http.route(['/report/barcode', '/report/barcode/<type>/<path:value>'], type='http', auth="public")
    def report_barcode(self, type, value, width=600, height=100, humanreadable=0, scale=1.0):
        if hasattr(pyzint.Barcode, type):
            try:
                symbol = getattr(pyzint.Barcode, type)(value, height=int(height), scale=float(scale)) # width is not a valid argument for pyzint, but generally you can use css styles for this
                return symbol.render_bmp()
            except (ValueError, AttributeError):
                raise werkzeug.exceptions.HTTPException(description='Cannot convert into barcode.')
        else:
            return super(ReportControllerExtraBarcodes, self).report_barcode(type=type, value=value, width=width, height=height, humanreadable=humanreadable)
