from os.path import join
import subprocess


class Autoresponse():
    """Autoresponse for payment"""
    data = None
    path_file = ""
    path_bin = ""

    def get_params(self):
        # Recuperation de la variable cryptee DATA
        message = "message=" + self.data

        # Initialisation du chemin du fichier pathfile
        pathfile = "pathfile=" + self.path_file

        # Initialisation du chemin de l'executable response
        path_bin = join(self.path_bin, "response_2.6.9_3.4.2")

        return (path_bin, pathfile, message)

    def call_autoresponse(self):
        # Recuperation des paranetre du binaire
        parm = self.get_params()

        # Appel du binaire response
        result = subprocess.Popen([p for p in parm], stdout=subprocess.PIPE).communicate()
        #  Sortie de la fonction : !code!error!v1!v2!v3!...!v29
        #      - code=0    : la fonction retourne les donnees de la transaction dans les variables v1, v2, ...
        #              : Ces variables sont decrites dans le GUIDE DU PROGRAMMEUR
        #      - code=-1   : La fonction retourne un message d'erreur dans la variable error
        #
        #  on separe les differents champs et on les met dans une variable tableau
        tab = result[0].split('!')

        # Recuperation des donnees de la reponse
        code_dict = {
            "code": tab[1],
            "error": tab[2],
            "merchant_id": tab[3],
            "merchant_country": tab[4],
            "amount": tab[5],
            "transaction_id": tab[6],
            "payment_means": tab[7],
            "transmission_date":tab[8],
            "payment_time": tab[9],
            "payment_date": tab[10],
            "response_code": tab[11],
            "payment_certificate": tab[12],
            "authorisation_id": tab[13],
            "currency_code": tab[14],
            "card_number": tab[15],
            "cvv_flag": tab[16],
            "cvv_response_code": tab[17],
            "bank_response_code": tab[18],
            "complementary_code": tab[19],
            "complementary_info": tab[20],
            "return_context": tab[21],
            "caddie": tab[22],
            "receipt_complement": tab[23],
            "merchant_language": tab[24],
            "language": tab[25],
            "customer_id": tab[26],
            "order_id": tab[27],
            "customer_email": tab[28],
            "customer_ip_address": tab[29],
            "capture_day": tab[30],
            "capture_mode": tab[31],
            "data": tab[32],
            "exec_path": parm[0],
        }

        return code_dict
