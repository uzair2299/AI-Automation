package com.smiota.common.dto.user;

import com.smiota.common.enums.Status;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserSummaryDto implements Serializable {
    private UUID id;
    private String username;
    private String email;
    private String fullName;
    private Status status;
}
