/**
 * Canonical 15 Supported Countries & Map Cartography Constants.
 */

export interface SupportedCountryMeta {
  code: string;
  name: string;
  display_name: string;
  region: string;
  lat: number;
  lng: number;
  zoom: number;
  primary_folklore_creature: string;
  primary_urban_legend: string;
  has_archive: true;
}

export const SUPPORTED_COUNTRIES: Record<string, SupportedCountryMeta> = {
  IN: {
    code: "IN",
    name: "India",
    display_name: "Republic of India (Bhārat)",
    region: "South Asia",
    lat: 20.5937,
    lng: 78.9629,
    zoom: 5,
    primary_folklore_creature: "Betal & Yakshini",
    primary_urban_legend: "Nale Ba & Sanjay Gandhi National Park Hitchhiker",
    has_archive: true,
  },
  US: {
    code: "US",
    name: "United States",
    display_name: "United States of America",
    region: "North America",
    lat: 37.0902,
    lng: -95.7129,
    zoom: 4,
    primary_folklore_creature: "Wendigo & Jersey Devil",
    primary_urban_legend: "Mothman & The Babysitter",
    has_archive: true,
  },
  JP: {
    code: "JP",
    name: "Japan",
    display_name: "Japan (Nihon / Nippon)",
    region: "East Asia",
    lat: 36.2048,
    lng: 138.2529,
    zoom: 5,
    primary_folklore_creature: "Kappa & Kitsune",
    primary_urban_legend: "Kuchisake-onna & Teke Teke",
    has_archive: true,
  },
  MX: {
    code: "MX",
    name: "Mexico",
    display_name: "United Mexican States",
    region: "Latin America",
    lat: 23.6345,
    lng: -102.5528,
    zoom: 5,
    primary_folklore_creature: "La Llorona & Nahual",
    primary_urban_legend: "La Planchada & El Chupacabra",
    has_archive: true,
  },
  IE: {
    code: "IE",
    name: "Ireland",
    display_name: "Ireland (Éire)",
    region: "Western Europe",
    lat: 53.1424,
    lng: -7.6921,
    zoom: 6,
    primary_folklore_creature: "Banshee & Púca",
    primary_urban_legend: "Hellfire Club & Black Dog of Killakee",
    has_archive: true,
  },
  GB: {
    code: "GB",
    name: "United Kingdom",
    display_name: "United Kingdom of Great Britain",
    region: "Western Europe",
    lat: 55.3781,
    lng: -3.436,
    zoom: 5,
    primary_folklore_creature: "Black Shuck & Green Man",
    primary_urban_legend: "Highgate Vampire & Spring-Heeled Jack",
    has_archive: true,
  },
  BR: {
    code: "BR",
    name: "Brazil",
    display_name: "Federative Republic of Brazil",
    region: "South America",
    lat: -14.235,
    lng: -51.9253,
    zoom: 4,
    primary_folklore_creature: "Saci-Pererê & Curupira",
    primary_urban_legend: "Loira do Banheiro & Chupa-Cabra",
    has_archive: true,
  },
  GR: {
    code: "GR",
    name: "Greece",
    display_name: "Hellenic Republic",
    region: "Southern Europe",
    lat: 39.0742,
    lng: 21.8243,
    zoom: 6,
    primary_folklore_creature: "Kallikantzaroi & Vrykolakas",
    primary_urban_legend: "Davelis Cave & Phantom of the Acropolis",
    has_archive: true,
  },
  CN: {
    code: "CN",
    name: "China",
    display_name: "People's Republic of China",
    region: "East Asia",
    lat: 35.8617,
    lng: 104.1954,
    zoom: 4,
    primary_folklore_creature: "Jiangshi & Huli Jing",
    primary_urban_legend: "Midnight Bus 375 & Chaonei No. 81",
    has_archive: true,
  },
  NG: {
    code: "NG",
    name: "Nigeria",
    display_name: "Federal Republic of Nigeria",
    region: "West Africa",
    lat: 9.082,
    lng: 8.6753,
    zoom: 6,
    primary_folklore_creature: "Eshu Trickster & Mami Wata",
    primary_urban_legend: "Madam Koi Koi & Bush Baby",
    has_archive: true,
  },
  KR: {
    code: "KR",
    name: "South Korea",
    display_name: "Republic of Korea",
    region: "East Asia",
    lat: 35.9078,
    lng: 127.7669,
    zoom: 6,
    primary_folklore_creature: "Gumiho & Dokkaebi",
    primary_urban_legend: "Jayu-ro Phantom & Red Toilet Paper Ghost",
    has_archive: true,
  },
  PH: {
    code: "PH",
    name: "Philippines",
    display_name: "Republic of the Philippines",
    region: "Southeast Asia",
    lat: 12.8797,
    lng: 121.774,
    zoom: 5,
    primary_folklore_creature: "Aswang & Tikbalang",
    primary_urban_legend: "White Lady of Balete Drive & Manila Film Center",
    has_archive: true,
  },
  ID: {
    code: "ID",
    name: "Indonesia",
    display_name: "Republic of Indonesia",
    region: "Southeast Asia",
    lat: -0.7893,
    lng: 113.9213,
    zoom: 5,
    primary_folklore_creature: "Kuntilanak & Pocong",
    primary_urban_legend: "Ambulance Ghost of Bandung & Jeruk Purut",
    has_archive: true,
  },
  EG: {
    code: "EG",
    name: "Egypt",
    display_name: "Arab Republic of Egypt",
    region: "North Africa",
    lat: 26.8206,
    lng: 30.8025,
    zoom: 5,
    primary_folklore_creature: "Aisha Qandisha & El Naddaha",
    primary_urban_legend: "Curse of the Pharaohs & Baron Empain Palace",
    has_archive: true,
  },
  DE: {
    code: "DE",
    name: "Germany",
    display_name: "Federal Republic of Germany",
    region: "Central Europe",
    lat: 51.1657,
    lng: 10.4515,
    zoom: 6,
    primary_folklore_creature: "Erlkönig & Lorelei",
    primary_urban_legend: "Bielefeld Conspiracy & White Lady of Hohenzollern",
    has_archive: true,
  },
};

export const SUPPORTED_COUNTRY_CODES = Object.keys(SUPPORTED_COUNTRIES);

export function isCountrySupported(code: string): boolean {
  return SUPPORTED_COUNTRY_CODES.includes(code.toUpperCase());
}

export const UNSUPPORTED_COUNTRY_NOTICE = {
  badge: "Stories coming soon",
  message:
    "Our archive is still growing. Folklore and urban legends from this country will be available soon.",
};
