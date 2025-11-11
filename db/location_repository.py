from db.postgres_client import PostgresClient
from models.location import Location
from models.offer import Offer


class LocationRepository:
    def __init__(self, client: PostgresClient):
        self.client = client

    def save_location(self, location: Location):
        sql = """
            INSERT INTO locations (judet, zona, lat, lng)
            VALUES (%(judet)s, %(zona)s, %(lat)s, %(lng)s)
            RETURNING id, judet, zona, lat, lng
        """
        params = {
            "judet": location.judet,
            "zona": location.zona,
            "lat": location.lat,
            "lng": location.lng
        }
        with self.client.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                conn.commit()
                return Location(
                    id=row["id"],
                    judet=row["judet"],
                    zona=row["zona"],
                    lat=row["lat"],
                    lng=row["lng"]
                )

    def find_location_by_judet_and_zona(self, offer: Offer)->Location | None:
        sql = """
            SELECT id, judet, zona, lat, lng
            FROM locations
            WHERE judet = %(judet)s
            AND zona = %(zona)s
        """
        params = {"judet": offer.judet, "zona": offer.zona}
        with self.client.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                result = cur.fetchone()
                if result:
                    return Location(
                        id=result["id"],
                        judet=result["judet"],
                        zona=result["zona"],
                        lat=result["lat"],
                        lng=result["lng"]
                    )
                return None
