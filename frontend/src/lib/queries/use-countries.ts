import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export function useCountries() {
  return useQuery({
    queryKey: ["countries"],
    queryFn: () => api.listCountries({ limit: 50 }),
  });
}

export function useCountry(code: string) {
  return useQuery({
    queryKey: ["country", code],
    queryFn: () => api.getCountry(code),
    enabled: Boolean(code),
  });
}

export function useCountryStats(code: string) {
  return useQuery({
    queryKey: ["country-stats", code],
    queryFn: () => api.getCountryStats(code),
    enabled: Boolean(code),
  });
}

