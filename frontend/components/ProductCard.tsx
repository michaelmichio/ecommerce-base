import Image from "next/image";
import { Product } from "@/types/product";
import { Card, CardHeader, CardContent } from "@/components/ui/card";

export default function ProductCard({ product }: { product: Product }) {
  const image = product.images?.[0] || "/placeholder.png";

  return (
    <Card className="hover:shadow-md transition-all cursor-pointer">
      <CardHeader>
        <Image
          src={image}
          alt={product.name}
          width={400}
          height={300}
          className="w-full h-48 object-cover rounded-lg"
        />
      </CardHeader>
      <CardContent className="flex flex-col gap-1">
        <h3 className="font-semibold text-lg">{product.name}</h3>
        <p className="text-sm text-gray-500">{product.category}</p>
        <p className="font-bold text-primary">${product.price.toFixed(2)}</p>
      </CardContent>
    </Card>
  );
}
