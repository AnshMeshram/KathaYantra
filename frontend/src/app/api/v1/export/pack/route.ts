import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/server/repository";
import { isCountrySupported } from "@/constants/countries";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  const category = searchParams.get("category") || undefined;
  const country_code = searchParams.get("country_code") || undefined;

  if (category && category !== "folklore" && category !== "urban_legend") {
    return NextResponse.json(
      {
        message: "Invalid category. Must be 'folklore' or 'urban_legend'.",
        error_code: "INVALID_CATEGORY",
      },
      { status: 422 }
    );
  }

  if (country_code && !isCountrySupported(country_code.toUpperCase())) {
    return NextResponse.json(
      {
        message: `Country ${country_code} is not in the supported archive.`,
        error_code: "COUNTRY_NOT_SUPPORTED",
      },
      { status: 404 }
    );
  }

  try {
    const pack = await repository.createArchivePackZip({
      category,
      country_code,
    });

    return new Response(new Uint8Array(pack.buffer), {
      status: 200,
      headers: {
        "Content-Type": "application/zip",
        "Content-Disposition": `attachment; filename="${pack.filename}"`,
        "X-Archive-Count": String(pack.count),
        "Cache-Control": "public, max-age=3600",
      },
    });
  } catch (err: any) {
    return NextResponse.json(
      {
        message: err.message || "Failed to generate archive pack",
        error_code: "EXPORT_ERROR",
      },
      { status: 500 }
    );
  }
}
