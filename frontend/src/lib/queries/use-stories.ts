import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { Category } from "@/types/story";

export function useFolklore(
  params: { country_code?: string; limit?: number; offset?: number } = {},
) {
  return useQuery({
    queryKey: ["folklore", params],
    queryFn: () => api.listFolklore(params),
  });
}

export function useUrbanLegends(
  params: { country_code?: string; limit?: number; offset?: number } = {},
) {
  return useQuery({
    queryKey: ["urban-legends", params],
    queryFn: () => api.listUrbanLegends(params),
  });
}

export function useStory(id: string) {
  return useQuery({
    queryKey: ["story", id],
    queryFn: () => api.getStory(id),
    enabled: Boolean(id),
  });
}

export function useStorySources(id: string) {
  return useQuery({
    queryKey: ["story-sources", id],
    queryFn: () => api.getStorySources(id),
    enabled: Boolean(id),
  });
}

export function useRelatedStories(id: string, limit: number = 5) {
  return useQuery({
    queryKey: ["story-related", id, limit],
    queryFn: () => api.getRelatedStories(id, limit),
    enabled: Boolean(id),
  });
}
