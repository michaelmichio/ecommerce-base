import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { ProductListResponse } from "@/types/response";

interface Params {
  page?: number;
  limit?: number;
  sort?: string;
}

export function useProducts(params: Params) {
  return useQuery({
    queryKey: ["products", params],
    queryFn: async () => {
      const { data } = await api.get<ProductListResponse>("/products", {
        params,
      });
      return data.data;
    },
  });
}
