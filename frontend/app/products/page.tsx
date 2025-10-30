"use client";

import { useState } from "react";
import { useProducts } from "@/hooks/useProducts";
import ProductCard from "@/components/ProductCard";
import Pagination from "@/components/Pagination";
import { LogoutButton } from "@/components/LogoutButton";
import AuthLayout from "@/components/layouts/AuthLayout";

export default function ProductsPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading, error } = useProducts({
    page,
    limit: 8,
    sort: "created_desc",
  });

  if (isLoading) return <p className="text-center mt-10">Loading...</p>;
  if (error)
    return (
      <p className="text-center text-red-500">
        Error: {(error as Error).message}
      </p>
    );

  return (
    <AuthLayout>
      <div className="max-w-6xl mx-auto py-10">
        <h1 className="text-2xl font-bold mb-6">Products</h1>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {data?.items?.map((product: any) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>

        <Pagination
          page={data?.page ?? 1}
          pages={data?.pages ?? 1}
          onPageChange={setPage}
        />
      </div>
    </AuthLayout>
  );
}
