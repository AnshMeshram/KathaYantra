import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/server/repository";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  const query = searchParams.get("q") || "";
  const category = searchParams.get("category") || undefined;
  const country_code = searchParams.get("country_code") || undefined;
  const limit = parseInt(searchParams.get("limit") || "20", 10);
  const offset = parseInt(searchParams.get("offset") || "0", 10);
  const page = Math.floor(offset / limit) + 1;

  const result = repository.getStories({
    category,
    country_code,
    search: query,
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
