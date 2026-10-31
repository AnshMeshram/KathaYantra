import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/server/repository";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  const country_code = searchParams.get("country_code") || undefined;
  const search = searchParams.get("q") || undefined;
  const limit = parseInt(searchParams.get("limit") || "150", 10);
  const offset = parseInt(searchParams.get("offset") || "0", 10);
  const page = Math.floor(offset / limit) + 1;

  const result = repository.getStories({
    category: "urban_legend",
    country_code,
    search,
    page,
    limit,
  });

  return NextResponse.json({
    data: result.data,
    pagination: {
      total: result.total,
      page: result.page,
      limit: result.limit,
      pages: result.pages,
    },
  });
}
