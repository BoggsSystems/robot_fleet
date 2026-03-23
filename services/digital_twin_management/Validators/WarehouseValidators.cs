using FluentValidation;
using WarehouseDigitalTwin.Models;

namespace WarehouseDigitalTwin.Validators;

/// <summary>
/// Validator for WarehouseDigitalTwin model
/// </summary>
public class WarehouseDigitalTwinValidator : AbstractValidator<WarehouseDigitalTwin>
{
    public WarehouseDigitalTwinValidator()
    {
        RuleFor(w => w.Id)
            .NotEmpty()
            .WithMessage("Warehouse ID is required")
            .Matches(@"^[a-zA-Z0-9\-_]+$")
            .WithMessage("Warehouse ID can only contain alphanumeric characters, hyphens, and underscores");

        RuleFor(w => w.Name)
            .NotEmpty()
            .WithMessage("Warehouse name is required")
            .MinimumLength(3)
            .WithMessage("Warehouse name must be at least 3 characters long")
            .MaximumLength(100)
            .WithMessage("Warehouse name cannot exceed 100 characters");

        RuleFor(w => w.Description)
            .MaximumLength(500)
            .WithMessage("Warehouse description cannot exceed 500 characters");

        RuleFor(w => w.TotalArea)
            .GreaterThan(0)
            .WithMessage("Warehouse total area must be greater than 0");

        RuleFor(w => w.Zones)
            .NotNull()
            .WithMessage("Zones collection is required")
            .Must(zones => zones.Count > 0)
            .WithMessage("Warehouse must have at least one zone");

        RuleFor(w => w.Robots)
            .NotNull()
            .WithMessage("Robots collection is required")
            .Must(robots => robots.Count > 0)
            .WithMessage("Warehouse must have at least one robot");

        RuleForEach(w => w.Zones)
            .SetValidator(new ZoneValidator());

        RuleForEach(w => w.Robots)
            .SetValidator(new RobotValidator());
    }
}

/// <summary>
/// Validator for Zone model
/// </summary>
public class ZoneValidator : AbstractValidator<Zone>
{
    public ZoneValidator()
    {
        RuleFor(z => z.Id)
            .NotEmpty()
            .WithMessage("Zone ID is required")
            .Matches(@"^[a-zA-Z0-9\-_]+$")
            .WithMessage("Zone ID can only contain alphanumeric characters, hyphens, and underscores");

        RuleFor(z => z.Name)
            .NotEmpty()
            .WithMessage("Zone name is required")
            .MinimumLength(2)
            .WithMessage("Zone name must be at least 2 characters long")
            .MaximumLength(50)
            .WithMessage("Zone name cannot exceed 50 characters");

        RuleFor(z => z.Area)
            .GreaterThan(0)
            .WithMessage("Zone area must be greater than 0");

        RuleFor(z => z.Capacity)
            .GreaterThan(0)
            .WithMessage("Zone capacity must be greater than 0");

        RuleFor(z => z.CurrentOccupancy)
            .GreaterThanOrEqualTo(0)
            .WithMessage("Zone current occupancy cannot be negative");

        RuleFor(z => z.CurrentOccupancy)
            .LessThanOrEqualTo(z => z.Capacity)
            .WithMessage("Zone current occupancy cannot exceed capacity");

        RuleFor(z => z.Temperature)
            .InclusiveBetween(-20, 50)
            .WithMessage("Zone temperature must be between -20°C and 50°C");

        RuleFor(z => z.Humidity)
            .InclusiveBetween(0, 100)
            .WithMessage("Zone humidity must be between 0% and 100%");

        RuleFor(z => z.BusinessRules)
            .NotNull()
            .WithMessage("Business rules collection is required");

        RuleForEach(z => z.BusinessRules)
            .SetValidator(new BusinessRuleValidator());
    }
}

/// <summary>
/// Validator for RobotAsset model
/// </summary>
public class RobotValidator : AbstractValidator<RobotAsset>
{
    public RobotValidator()
    {
        RuleFor(r => r.Id)
            .NotEmpty()
            .WithMessage("Robot ID is required")
            .Matches(@"^[a-zA-Z0-9\-_]+$")
            .WithMessage("Robot ID can only contain alphanumeric characters, hyphens, and underscores");

        RuleFor(r => r.Name)
            .NotEmpty()
            .WithMessage("Robot name is required")
            .MinimumLength(2)
            .WithMessage("Robot name must be at least 2 characters long")
            .MaximumLength(50)
            .WithMessage("Robot name cannot exceed 50 characters");

        RuleFor(r => r.BatteryPct)
            .InclusiveBetween(0, 100)
            .WithMessage("Robot battery percentage must be between 0 and 100");

        RuleFor(r => r.Capabilities)
            .NotNull()
            .WithMessage("Robot capabilities collection is required")
            .Must(capabilities => capabilities.Count > 0)
            .WithMessage("Robot must have at least one capability");

        RuleForEach(r => r.Capabilities)
            .NotEmpty()
            .WithMessage("Robot capability cannot be empty");

        RuleFor(r => r.Location)
            .NotNull()
            .WithMessage("Robot location is required")
            .SetValidator(new LocationValidator());
    }
}

/// <summary>
/// Validator for Location model
/// </summary>
public class LocationValidator : AbstractValidator<Location>
{
    public LocationValidator()
    {
        RuleFor(l => l.Floor)
            .GreaterThan(0)
            .WithMessage("Floor number must be greater than 0");
    }
}

/// <summary>
/// Validator for Workstation model
/// </summary>
public class WorkstationValidator : AbstractValidator<Workstation>
{
    public WorkstationValidator()
    {
        RuleFor(w => w.Id)
            .NotEmpty()
            .WithMessage("Workstation ID is required")
            .Matches(@"^[a-zA-Z0-9\-_]+$")
            .WithMessage("Workstation ID can only contain alphanumeric characters, hyphens, and underscores");

        RuleFor(w => w.Name)
            .NotEmpty()
            .WithMessage("Workstation name is required")
            .MinimumLength(2)
            .WithMessage("Workstation name must be at least 2 characters long")
            .MaximumLength(50)
            .WithMessage("Workstation name cannot exceed 50 characters");

        RuleFor(w => w.Location)
            .NotNull()
            .WithMessage("Workstation location is required")
            .SetValidator(new LocationValidator());
    }
}

/// <summary>
/// Validator for Conveyor model
/// </summary>
public class ConveyorValidator : AbstractValidator<Conveyor>
{
    public ConveyorValidator()
    {
        RuleFor(c => c.Id)
            .NotEmpty()
            .WithMessage("Conveyor ID is required")
            .Matches(@"^[a-zA-Z0-9\-_]+$")
            .WithMessage("Conveyor ID can only contain alphanumeric characters, hyphens, and underscores");

        RuleFor(c => c.Name)
            .NotEmpty()
            .WithMessage("Conveyor name is required")
            .MinimumLength(2)
            .WithMessage("Conveyor name must be at least 2 characters long")
            .MaximumLength(50)
            .WithMessage("Conveyor name cannot exceed 50 characters");

        RuleFor(c => c.Speed)
            .GreaterThan(0)
            .WithMessage("Conveyor speed must be greater than 0");

        RuleFor(c => c.Capacity)
            .GreaterThan(0)
            .WithMessage("Conveyor capacity must be greater than 0");

        RuleFor(c => c.CurrentLoad)
            .GreaterThanOrEqualTo(0)
            .WithMessage("Conveyor current load cannot be negative");

        RuleFor(c => c.CurrentLoad)
            .LessThanOrEqualTo(c => c.Capacity)
            .WithMessage("Conveyor current load cannot exceed capacity");

        RuleFor(c => c.StartLocation)
            .NotEmpty()
            .WithMessage("Conveyor start location is required");

        RuleFor(c => c.EndLocation)
            .NotEmpty()
            .WithMessage("Conveyor end location is required")
            .NotEqual(c => c.StartLocation)
            .WithMessage("Conveyor end location must be different from start location");
    }
}

/// <summary>
/// Validator for DockingBay model
/// </summary>
public class DockingBayValidator : AbstractValidator<DockingBay>
{
    public DockingBayValidator()
    {
        RuleFor(d => d.Id)
            .NotEmpty()
            .WithMessage("Docking bay ID is required")
            .Matches(@"^[a-zA-Z0-9\-_]+$")
            .WithMessage("Docking bay ID can only contain alphanumeric characters, hyphens, and underscores");

        RuleFor(d => d.Name)
            .NotEmpty()
            .WithMessage("Docking bay name is required")
            .MinimumLength(2)
            .WithMessage("Docking bay name must be at least 2 characters long")
            .MaximumLength(50)
            .WithMessage("Docking bay name cannot exceed 50 characters");

        RuleFor(d => d.Location)
            .NotNull()
            .WithMessage("Docking bay location is required")
            .SetValidator(new LocationValidator());

        RuleFor(d => d.EstimatedArrival)
            .LessThanOrEqualTo(d => d.EstimatedDeparture)
            .When(d => d.EstimatedArrival.HasValue && d.EstimatedDeparture.HasValue)
            .WithMessage("Estimated arrival must be before or equal to estimated departure");
    }
}

/// <summary>
/// Validator for BusinessRule model
/// </summary>
public class BusinessRuleValidator : AbstractValidator<BusinessRule>
{
    public BusinessRuleValidator()
    {
        RuleFor(br => br.RuleId)
            .NotEmpty()
            .WithMessage("Business rule ID is required")
            .Matches(@"^[a-zA-Z0-9\-_]+$")
            .WithMessage("Business rule ID can only contain alphanumeric characters, hyphens, and underscores");

        RuleFor(br => br.Name)
            .NotEmpty()
            .WithMessage("Business rule name is required")
            .MinimumLength(2)
            .WithMessage("Business rule name must be at least 2 characters long")
            .MaximumLength(100)
            .WithMessage("Business rule name cannot exceed 100 characters");

        RuleFor(br => br.Description)
            .MaximumLength(500)
            .WithMessage("Business rule description cannot exceed 500 characters");

        RuleFor(br => br.Conditions)
            .NotNull()
            .WithMessage("Business rule conditions collection is required")
            .Must(conditions => conditions.Count > 0)
            .WithMessage("Business rule must have at least one condition");

        RuleFor(br => br.Actions)
            .NotNull()
            .WithMessage("Business rule actions collection is required")
            .Must(actions => actions.Count > 0)
            .WithMessage("Business rule must have at least one action");

        RuleForEach(br => br.Conditions)
            .SetValidator(new RuleConditionValidator());

        RuleForEach(br => br.Actions)
            .SetValidator(new RuleActionValidator());
    }
}

/// <summary>
/// Validator for RuleCondition model
/// </summary>
public class RuleConditionValidator : AbstractValidator<RuleCondition>
{
    public RuleConditionValidator()
    {
        RuleFor(rc => rc.Property)
            .NotEmpty()
            .WithMessage("Rule condition property is required");

        RuleFor(rc => rc.Operator)
            .NotEmpty()
            .WithMessage("Rule condition operator is required")
            .Must(op => new[] { "=", "!=", ">", "<", ">=", "<=", "in", "not_in", "contains", "not_contains" }.Contains(op))
            .WithMessage("Invalid rule condition operator");

        RuleFor(rc => rc.Value)
            .NotNull()
            .WithMessage("Rule condition value is required");
    }
}

/// <summary>
/// Validator for RuleAction model
/// </summary>
public class RuleActionValidator : AbstractValidator<RuleAction>
{
    public RuleActionValidator()
    {
        RuleFor(ra => ra.ActionType)
            .NotEmpty()
            .WithMessage("Rule action type is required")
            .Must(type => new[] { "alert", "reallocate", "stop", "redirect", "log", "notify" }.Contains(type))
            .WithMessage("Invalid rule action type");

        RuleFor(ra => ra.Parameters)
            .NotNull()
            .WithMessage("Rule action parameters collection is required");
    }
}
