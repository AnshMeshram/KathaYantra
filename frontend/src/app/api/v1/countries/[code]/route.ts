import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/server/repository";

export async function GET(
  _request: NextRequest,
  { params }: { params: { code: string } }
) {
  const code = params.code?.toUpperCase();
  const country = repository.getCountry(code);

  if (!country) {
    return NextResponse.json(
      {
        message: `Country ${code} not supported or not found`,
        error_code: "COUNTRY_NOT_FOUND",
      },
      { status: 404 }
    );
  }

  return NextResponse.json({
    data: country,
  });
}
