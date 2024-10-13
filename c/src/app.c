#include "raylib.h"
#include <stdio.h>

#define CELL_SIZE 60
#define ROWS 10
#define COLS 10

int main(void)
{
    // Initialization
    const int screenWidth = COLS * CELL_SIZE;
    const int screenHeight = ROWS * CELL_SIZE;
    InitWindow(screenWidth, screenHeight, "Simple Spreadsheet GUI");

    int cells[ROWS][COLS] = { 0 };  // Stores the value of each cell
    int selectedRow = 0, selectedCol = 0;
    char inputText[32] = "";  // Store input text for the cell
    bool editing = false;  // Whether we're editing a cell

    SetTargetFPS(60);

    // Main game loop
    while (!WindowShouldClose())
    {
        // Input Handling
        if (IsKeyPressed(KEY_RIGHT)) selectedCol = (selectedCol + 1) % COLS;
        if (IsKeyPressed(KEY_LEFT)) selectedCol = (selectedCol - 1 + COLS) % COLS;
        if (IsKeyPressed(KEY_DOWN)) selectedRow = (selectedRow + 1) % ROWS;
        if (IsKeyPressed(KEY_UP)) selectedRow = (selectedRow - 1 + ROWS) % ROWS;

        if (IsKeyPressed(KEY_ENTER))
        {
            if (editing)
            {
                cells[selectedRow][selectedCol] = atoi(inputText);  // Save value
                inputText[0] = '\0';  // Clear input
            }
            editing = !editing;
        }

        if (editing)
        {
            int key = GetCharPressed();
            while (key > 0)
            {
                if ((key >= 32) && (key <= 125) && (strlen(inputText) < sizeof(inputText) - 1))
                {
                    int len = strlen(inputText);
                    inputText[len] = (char)key;
                    inputText[len + 1] = '\0';
                }
                key = GetCharPressed();
            }
            if (IsKeyPressed(KEY_BACKSPACE) && (strlen(inputText) > 0))
            {
                inputText[strlen(inputText) - 1] = '\0';
            }
        }

        // Drawing
        BeginDrawing();
        ClearBackground(RAYWHITE);

        // Draw grid and cell values
        for (int row = 0; row < ROWS; row++)
        {
            for (int col = 0; col < COLS; col++)
            {
                Rectangle cell = { col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE };
                DrawRectangleLinesEx(cell, 2, LIGHTGRAY);

                if (row == selectedRow && col == selectedCol)
                {
                    DrawRectangleRec(cell, Fade(SKYBLUE, 0.5f));
                }

                if (!(editing && row == selectedRow && col == selectedCol))
                {
                    char value[32];
                    sprintf(value, "%d", cells[row][col]);
                    DrawText(value, cell.x + 10, cell.y + 10, 20, BLACK);
                }
            }
        }

        // Draw input text if editing
        if (editing)
        {
            DrawText(inputText, selectedCol * CELL_SIZE + 10, selectedRow * CELL_SIZE + 10, 20, RED);
        }

        EndDrawing();
    }

    // De-Initialization
    CloseWindow();

    return 0;
}
