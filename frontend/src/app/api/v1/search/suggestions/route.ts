import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/server/repository";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get("q") || "";
  const limit = parseInt(searchParams.get("limit") || "10", 10);

  const suggestions = repository.suggest(query, limit);

  return NextResponse.json({
    data: suggestions,
  });
}
