from db.postgres_client import PostgresClient
from models.offer import Offer


class OfferRepository:
    def __init__(self, client: PostgresClient):
        self.client = client
        self.client.init_schema()

    def save_offer(self, offer: Offer):
        sql = """
                INSERT INTO offers (
                    url, sursa, titlu, pret, judet, oras, zona, lat, lng, 
                    descriere, data_postarii, tip_proprietate, tip_tranzactie, tip_vanzator, suprafata,
                    numar_camere, etaj, compartimentare, an_constructie, imagini, active
                )
                VALUES (
                    %(url)s, %(sursa)s, %(titlu)s, %(pret)s, %(judet)s, %(oras)s, %(zona)s, %(lat)s, %(lng)s, 
                    %(descriere)s, %(data_postarii)s, %(tip_proprietate)s, %(tip_tranzactie)s, %(tip_vanzator)s, %(suprafata)s,
                    %(numar_camere)s, %(etaj)s, %(compartimentare)s, %(an_constructie)s, %(imagini)s, %(active)s
                )
                ON CONFLICT (url) DO UPDATE SET
                    pret = EXCLUDED.pret,
                    judet = EXCLUDED.judet,
                    oras = EXCLUDED.oras,
                    zona = EXCLUDED.zona,
                    lat = EXCLUDED.lat,
                    lng = EXCLUDED.lng,
                    descriere = EXCLUDED.descriere,
                    data_postarii = EXCLUDED.data_postarii,
                    tip_proprietate = EXCLUDED.tip_proprietate,
                    tip_tranzactie = EXCLUDED.tip_tranzactie,
                    tip_vanzator = EXCLUDED.tip_vanzator,
                    suprafata = EXCLUDED.suprafata,
                    numar_camere = EXCLUDED.numar_camere,
                    etaj = EXCLUDED.etaj,
                    compartimentare = EXCLUDED.compartimentare,
                    an_constructie = EXCLUDED.an_constructie,
                    imagini = EXCLUDED.imagini,
                    active = EXCLUDED.active;
                """
        params = {
            "url": offer.url,
            "sursa": offer.sursa,
            "titlu": offer.titlu,
            "pret": offer.pret,
            "judet": offer.judet,
            "oras": offer.oras,
            "zona": offer.zona,
            "lat": offer.lat,
            "lng": offer.lng,
            "descriere": offer.descriere,
            "data_postarii": offer.data_postarii,
            "tip_proprietate": offer.tip_proprietate,
            "tip_tranzactie": offer.tip_tranzactie,
            "tip_vanzator": offer.tip_vanzator,
            "suprafata": offer.suprafata,
            "numar_camere": offer.numar_camere,
            "etaj": offer.etaj,
            "compartimentare": offer.compartimentare,
            "an_constructie": offer.an_constructie,
            "imagini": offer.imagini,
            "active": offer.active,
        }
        with self.client.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
