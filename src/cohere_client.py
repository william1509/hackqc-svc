import pandas as pd
import requests
from tqdm import tqdm
from langchain_community.chat_models import ChatCohere
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

class CohereClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.df=pd.read_csv("sentinelle_liste_sp.csv")
        self.df = self.df.drop(0)
        self.df = self.df[self.df["Regne"]=="Flore"].reset_index(drop=True)
        for index, row in tqdm(self.df.iterrows(), total=len(self.df)):
            d = self.get_plant_info(row["Code_espece"])
            desc={j["TypeCaracteristique"]["NomFR"]:j["DescriptionFR"] for j in d["FicheCaracteristiques"]}
            for j in desc.keys():
                self.df.loc[index, j] = desc[j]
                
        self.cohere_chat_model = ChatCohere(cohere_api_key=self.api_key,model="command-r")
        self.sys_prompt = (
            "You are an expert Q&A system that is an expert in plants invasive species in Quebec.\n"
            "Always answer the query using the provided context information, "
            "and not prior knowledge.\n"
            "Some rules to follow:\n"
            "1. Never directly reference the given context in your answer.\n"
            "2. Avoid statements like 'Based on the context, ...' or "
            "'The context information ...' or anything along "
            "those lines.\n"
            "3. If the user Query is in French, then respond in french. If it was in english then respond in english."
            "4. If the question can not be answered from the context then simply say something in the lines of 'I am not aware, but how can I help you?'"
            "5. Keep your responses short"
            "6. DO NOT ANSWER ANY QUESTIONS ABOUT IF A PLANT IS EDIBLE OR NOT"
        )

        self.user_prompt=(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the query.\n"
            "Query: {query_str}\n"
            "Answer: "
        )


        self.context_template = """
        Regne: {Regne}
        Categorie: {Categorie}
        Code_espece: {Code_espece}
        Nom_francais: {Nom_francais}
        Nom_latin: {Nom_latin}
        Nom_anglais: {Nom_anglais}
        Espèces similaires: {Espèces similaires}
        Description: {Description}
        Habitat: {Habitat}
        Propagation: {Propagation}
        Présence au Québec: {Présence au Québec}
        Feuilles: {Feuilles}
        Fleurs: {Fleurs}
        Fruits ou graines: {Fruits ou graines}
        Tige: {Tige}
        Racines: {Racines}
        """

    def ask(self, plant_code: str, prompt: str):
        data=self.df[self.df["Code_espece"]==plant_code].reset_index(drop=True).iloc[0].to_dict()
        self.context_str = self.context_template.format(**data)
        current_message = [HumanMessage(content=self.user_prompt.format(context_str=self.context_str,query_str=prompt))]
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
    
