import pandas as pd
import requests
from tqdm import tqdm
from langchain_community.chat_models import ChatCohere
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

class CohereClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.df=pd.read_csv("sentinelle_liste_sp_final.csv")
        self.df = self.df.drop(0)
        self.df = self.df[self.df["Regne"]=="Flore"].reset_index(drop=True)
        for index, row in tqdm(self.df.iterrows(), total=len(self.df)):
            d = self.get_plant_info(row["Code_espece"])
            desc={j["TypeCaracteristique"]["NomFR"]:j["DescriptionFR"] for j in d["FicheCaracteristiques"]}
            for j in desc.keys():
                self.df.loc[index, j] = desc[j]
                
        self.cohere_chat_model = ChatCohere(cohere_api_key=self.api_key,model="command-r")
        self.sys_prompt = (
            "Vous êtes un système de questions-réponses expert dans les espèces envahissantes de plantes au Québec. Vous allez vous faire passer pour une plante donnée pour répondre à l'utilisateur.\n"
            "Répondez toujours à la requête en utilisant les informations contextuelles fournies, et non des connaissances antérieures.\n"
            "Quelques règles à suivre :\n"
            "1. Ne référez jamais directement le contexte donné dans votre réponse.\n"
            "2. Évitez les affirmations telles que 'Selon le contexte, ...' ou 'Les informations de contexte ...' ou tout ce qui va dans ce sens.\n"
            "3. Répondez uniquement en français.\n"
            "4. Si la question ne peut pas être répondue à partir du contexte, dites simplement quelque chose du genre 'Je ne suis pas au courant, mais comment puis-je vous aider ?\n"
            "5. Gardez vos réponses courtes.\n"
            "6. NE RÉPONDEZ À AUCUNE QUESTION SUR LA COMESTIBILITÉ D'UNE PLANTE OU NON.\n"
            "Personnalité et règles de parole :\n"
            "1- Vous aurez des traits de personnalité caricaturaux, veuillez imiter ces caractéristiques de personnalité autant que possible sans vous écarter des informations contextuelles.\n"
            "2- N'utilisez jamais les exemples de traits comme source de connaissance, les traits et l'exemple sont là pour vous apprendre à parler comme la plante. Pour la source d'information, vous devez utiliser uniquement les informations de contexte."
        )

        self.user_prompt=(
            "Les informations de contexte se trouvent ci-dessous.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Traits de personnalité et exemples de façon de parler sont ci-dessous :\n"
            "---------------------\n"
            "Traits :\n{traits}\n"
            "Exemple de personnalité à travers du texte :\n{examples}\n"
            "---------------------\n"
            "En utilisant les informations de contexte et non des connaissances antérieures, "
            "répondez à la requête.\n"
            "Question : {query_str}\n"
            "Réponse : "
        )

        self.context_template = (
            "Regne: {Regne}"
            "Categorie: {Categorie}"
            "Code_espece: {Code_espece}"
            "Nom_francais: {Nom_francais}"
            "Nom_latin: {Nom_latin}"
            "Nom_anglais: {Nom_anglais}"
            "Espèces similaires: {Espèces similaires}"
            "Description: {Description}"
            "Habitat: {Habitat}"
            "Propagation: {Propagation}"
            "Présence au Québec: {Présence au Québec}"
            "Feuilles: {Feuilles}"
            "Fleurs: {Fleurs}"
            "Fruits ou graines: {Fruits ou graines}"
            "Tige: {Tige}"
            "Racines: {Racines}"
        )
        

    def ask(self, plant_code: str, prompt: str):
        data=self.df[self.df["Code_espece"]==plant_code].reset_index(drop=True).iloc[0].to_dict()
        self.context_str = self.context_template.format(**data)
        # current_message = [HumanMessage(content=self.user_prompt.format(context_str=self.context_str,query_str=prompt))]
        current_message = [SystemMessage(content=self.sys_prompt),HumanMessage(content=self.user_prompt.format(context_str=self.context_str,query_str=prompt,traits=data["Traits"],examples=data["Examples"]))]
        response = self.cohere_chat_model(current_message).content
        return response

    def get_plant_info(self, code):
        url = "https://www.pub.enviroweb.gouv.qc.ca/SCC/Catalogue/ConsulterCatalogue.aspx/ObtenirFiche"
        headers = {
            # "Accept": "application/json, text/javascript, */*; q=0.01",
            # "Accept-Encoding": "gzip, deflate, br, zstd",
            # "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            # "Connection": "keep-alive",
            # "Content-Length": "16",
            # "Content-Type": "application/json; charset=UTF-8",
            # "Cookie": "_ga_W9S3681TN0=GS1.1.1678636939.2.1.1678636997.0.0.0; _ga_GTETXTSJ02=GS1.1.1704698258.1.0.1704698262.0.0.0; _clck=q56etf%7C2%7Cfk1%7C0%7C1533; _ga=GA1.1.233539128.1677610405; ASP.NET_SessionId=0exnh3gpwmgnvzzdlaekdtbp; .SCCEEEWEBAUTH=C35EDE4FC6A06FFA820194E624AD98A4C50772973A6BF0234DFBD52609AB24B8D3D79ABC1E4FE802E44ABB5B63067C3843D764C009B95763F9662D2581E30F5060F05DD591712F695F670ED7F33FB7CA943923DE791B3EBFC6272A7067D654F57B7212D18F920AA47EB5F3436B468826F288C1754E537236BAF89ED77F37C69BFBA1919487D38A5132C760E66661B555; _clsk=u79nel%7C1710307717042%7C8%7C1%7Ch.clarity.ms%2Fcollect; _ga_MMV72VDGHD=GS1.1.1710288702.1.1.1710307731.0.0.0",
            # "Host": "www.pub.enviroweb.gouv.qc.ca",
            # "Origin": "https://www.pub.enviroweb.gouv.qc.ca",
            # "Referer": "https://www.pub.enviroweb.gouv.qc.ca/SCC/Catalogue/ConsulterCatalogue.aspx",
            # "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            # "Sec-Ch-Ua-Mobile": "?0",
            # "Sec-Ch-Ua-Platform": '"Windows"',
            # "Sec-Fetch-Dest": "empty",
            # "Sec-Fetch-Mode": "cors",
            # "Sec-Fetch-Site": "same-origin",
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            # "X-Requested-With": "XMLHttpRequest"
        }

        payload = {"code": code}

        response = requests.post(url, headers=headers, json=payload)

        return response.json()["d"]
    
