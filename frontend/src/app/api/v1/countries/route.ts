import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/server/repository";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const limit = parseInt(searchParams.get("limit") || "50", 10);
  const offset = parseInt(searchParams.get("offset") || "0", 10);

  const countries = repository.getCountries();
  const paginated = countries.slice(offset, offset + limit);

  return NextResponse.json({
    data: paginated,
    pagination: {
      total: countries.length,
      page: Math.floor(offset / limit) + 1,
      limit,
      pages: Math.ceil(countries.length / limit) || 1,
    },
  });
}
