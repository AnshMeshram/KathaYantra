import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/server/repository";

export async function GET(
  _request: NextRequest,
  { params }: { params: { code: string } }
) {
  const code = params.code?.toUpperCase();
  const stats = repository.getCountryStats(code);

  if (!stats) {
    return NextResponse.json(
      {
        message: `Country ${code} stats not available`,
        error_code: "COUNTRY_NOT_FOUND",
      },
      { status: 404 }
    );
  }

  return NextResponse.json({
    data: stats,
  });
}
