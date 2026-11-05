package com.smiota.common.dto.locker;

import com.smiota.common.enums.LockerState;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LockerUnitDto implements Serializable {
    private String unitId;
    private String bankId;
    private String lockerNumber;
    private LockerState state;
    private String size;
}
