import { NextRequest, NextResponse } from "next/server";
import { repository } from "@/lib/server/repository";

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  const story = repository.getStoryById(params.id?.toUpperCase());

  if (!story || story.category !== "folklore") {
    return NextResponse.json(
      {
        message: `Folklore story ${params.id} not found`,
        error_code: "STORY_NOT_FOUND",
      },
      { status: 404 }
    );
  }

  return NextResponse.json({
    data: story,
  });
}
