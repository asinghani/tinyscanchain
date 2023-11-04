`default_nettype none

module seven_segment_seconds #(
    parameter MAX_COUNT = 1000
) (
    input logic clk,
    input logic rst,
    input logic ena,
    output logic [6:0] led_out

);

    reg [$clog2(MAX_COUNT):0] second_counter;
    reg [3:0] digit;

    always @(posedge clk) begin
        // if reset, set counter to 0
        if (rst) begin
            second_counter <= 0;
            digit <= 0;
        end else begin
            // if up to 16e6
            if (second_counter == MAX_COUNT) begin
                // reset
                second_counter <= 0;

                // increment digit
                digit <= digit + 1'b1;

                // only count from 0 to 9
                if (digit == 9)
                    digit <= 0;

            end else begin
                // increment counter
                second_counter <= second_counter + 1'b1;
            end
        end
    end

    // instantiate segment display
    seg7 seg7(.counter(digit), .segments(led_out));

endmodule

module seg7 (
    input wire [3:0] counter,
    output reg [6:0] segments
);

    always @(*) begin
        case(counter)
            //                7654321
            0:  segments = 7'b0111111;
            1:  segments = 7'b0000110;
            2:  segments = 7'b1011011;
            3:  segments = 7'b1001111;
            4:  segments = 7'b1100110;
            5:  segments = 7'b1101101;
            6:  segments = 7'b1111101;
            7:  segments = 7'b0000111;
            8:  segments = 7'b1111111;
            9:  segments = 7'b1101111;
            10: segments = 7'b1110111;
            11: segments = 7'b1111100;
            12: segments = 7'b0111001;
            13: segments = 7'b1011110;
            14: segments = 7'b1111001;
            15: segments = 7'b1110001;
	    default:
                segments = 7'b0000000;
        endcase
    end

endmodule
